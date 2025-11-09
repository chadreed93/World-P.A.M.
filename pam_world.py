#!/usr/bin/env python3
"""
World P.A.M. — Predictive Analytic Machine for Global Scenarios
---------------------------------------------------------------
Evaluates geopolitical, environmental, and social risk hypotheses
based on live public RSS/Atom feeds (Reuters, BBC, UN, etc.).

Usage examples:
  python pam_world.py --list
  python pam_world.py --scenario global_war_risk --simulate 5000 --explain
  python pam_world.py --run-all
  python pam_world.py --help-info
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional
import json, math, random, argparse, sys, datetime
from urllib import request
import xml.etree.ElementTree as ET

# ---------- math helpers ----------
def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def logit(p: float) -> float:
    p = min(max(p, 1e-9), 1 - 1e-9)
    return math.log(p / (1 - p))

# ---------- data classes ----------
@dataclass
class SourceDef:
    name: str
    url: str
    type: str = "rss"
    timeout: float = 10.0

@dataclass
class SignalDef:
    name: str
    weight: float
    description: str = ""
    aggregation: str = "sum"
    cap: float = 1.0

@dataclass
class HypothesisDef:
    name: str
    prior: float
    signals: List[str]

@dataclass
class Config:
    sources: List[SourceDef]
    signals: List[SignalDef]
    hypotheses: List[HypothesisDef]
    keyword_sets: Dict[str, List[str]]
    signal_bindings: Dict[str, Dict[str, Any]]

# ---------- simple fetch + parse ----------
def fetch_url(url: str, timeout: float = 10.0) -> Optional[bytes]:
    try:
        with request.urlopen(url, timeout=timeout) as resp:
            return resp.read()
    except Exception:
        return None

def _text(node: Optional[ET.Element]) -> str:
    return (node.text or "").strip() if node is not None else ""

def parse_feed_bytes(feed_type: str, data: bytes) -> List[Dict[str, Any]]:
    items = []
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return items
    tag = "item" if feed_type == "rss" else "{http://www.w3.org/2005/Atom}entry"
    for entry in root.findall(f".//{tag}"):
        title = _text(entry.find("title"))
        summary = _text(entry.find("description")) or _text(entry.find("summary"))
        items.append({"title": title, "summary": summary})
    return items

def normalized_keyword_hits(items: List[Dict[str, Any]], keywords: List[str]) -> float:
    if not items or not keywords:
        return 0.0
    hits = 0
    for it in items:
        text = f"{it.get('title','')} {it.get('summary','')}".lower()
        if any(k.lower() in text for k in keywords):
            hits += 1
    # sqrt dampening
    return min(math.sqrt(hits) / math.sqrt(20.0), 1.0)

# ---------- main engine ----------
class WorldPAM:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.sources = {s.name: s for s in cfg.sources}
        self.signals = {s.name: s for s in cfg.signals}
        self.hyps = {h.name: h for h in cfg.hypotheses}

    def compute_signal(self, sig_name: str, country: Optional[str] = None) -> float:
        bind = self.cfg.signal_bindings.get(sig_name, {})
        srcs = bind.get("sources", [])
        kw_sets = bind.get("keywords", [])
        keywords = []
        for s in kw_sets:
            keywords += self.cfg.keyword_sets.get(s, [])
        if country:
            keywords.append(country)
        vals = []
        for src_name in srcs:
            src = self.sources[src_name]
            data = fetch_url(src.url, src.timeout)
            items = parse_feed_bytes(src.type, data or b"")
            vals.append(normalized_keyword_hits(items, keywords))
        if not vals:
            return 0.0
        sig = self.signals[sig_name]
        val = max(vals) if sig.aggregation == "max" else sum(vals)
        return min(val, sig.cap)

    def evaluate(self, hyp_name: str, country: Optional[str] = None, simulate: int = 0):
        hyp = self.hyps[hyp_name]
        z = logit(hyp.prior)
        details = []
        for s in hyp.signals:
            val = self.compute_signal(s, country)
            weight = self.signals[s].weight
            z += weight * val
            details.append((s, val, weight))
        p = sigmoid(z)
        if simulate:
            sims = []
            for _ in range(simulate):
                z2 = logit(hyp.prior)
                for s, val, w in details:
                    v = 1.0 if random.random() < val else 0.0
                    z2 += w * v
                sims.append(sigmoid(z2))
            sims.sort()
            mean = sum(sims) / len(sims)
            return p, mean, (sims[int(0.05*simulate)], sims[int(0.95*simulate)]), details
        return p, None, None, details

    def interpret(self, name: str, prob: float) -> str:
        if prob < 0.02:
            tone = "very low likelihood"
        elif prob < 0.1:
            tone = "low but notable likelihood"
        elif prob < 0.3:
            tone = "moderate risk that warrants attention"
        elif prob < 0.6:
            tone = "significant and rising probability"
        else:
            tone = "high probability—close watch advised"
        return f"P.A.M. assesses the scenario '{name}' with a {tone} ({prob*100:.1f}%)."

# ---------- util ----------
def load_config(path: str) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return Config(
        [SourceDef(**s) for s in raw["sources"]],
        [SignalDef(**s) for s in raw["signals"]],
        [HypothesisDef(**h) for h in raw["hypotheses"]],
        raw["keyword_sets"],
        raw["signal_bindings"]
    )

# ---------- CLI ----------
def help_info():
    print("""
World P.A.M. — Usage Guide
==========================
Examples:
  python pam_world.py --list
      Show all available hypotheses.

  python pam_world.py --scenario global_war_risk --simulate 5000 --explain
      Evaluate a single scenario with simulation and detailed signal output.

  python pam_world.py --country "Ukraine" --scenario civil_war_risk
      Add a country keyword bias to signal parsing.

  python pam_world.py --run-all
      Run every scenario and print readable summaries.

  python pam_world.py --help-info
      Show this help again.
    """)

def run_all(pam: WorldPAM, simulate: int = 0):
    print("Running all scenarios:\n")
    for name in pam.hyps:
        p, mean, ci, _ = pam.evaluate(name, simulate=simulate)
        line = f"{name:<28} → {p*100:5.1f}%"
        if ci:
            line += f" (avg {mean*100:4.1f}%, range {ci[0]*100:4.1f}–{ci[1]*100:4.1f}%)"
        print(line)
    print("\nTip: use --scenario <name> --explain for detailed breakdowns.\n")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", default="world_config.json")
    parser.add_argument("--scenario")
    parser.add_argument("--country")
    parser.add_argument("--simulate", type=int, default=0)
    parser.add_argument("--explain", action="store_true")
    parser.add_argument("--run-all", action="store_true")
    parser.add_argument("--help-info", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.help_info:
        help_info()
        return

    cfg = load_config(args.config)
    pam = WorldPAM(cfg)

    if args.list:
        print("Available scenarios:\n" + "\n".join(f" - {h.name}" for h in cfg.hypotheses))
        return

    if args.run_all:
        run_all(pam, simulate=args.simulate)
        return

    if not args.scenario:
        print("No scenario given. Use --list or --help-info.")
        return

    p, mean, ci, details = pam.evaluate(args.scenario, args.country, simulate=args.simulate)

    print("\n" + pam.interpret(args.scenario, p))
    if mean and ci:
        print(f"Monte Carlo mean: {mean*100:.1f}% (5–95% CI {ci[0]*100:.1f}%–{ci[1]*100:.1f}%)")
    if args.explain:
        print("\nSignal contributions:")
        for name, val, w in details:
            print(f"  {name:24s}  value={val:4.2f}  weight={w:+.2f}  → {val*w:+.3f}")
    print()

if __name__ == "__main__":
    main()
