"""Run with: python -m eve <command>."""
import argparse
import json
from pathlib import Path
from .core import Memory, make_proposal
from .exchange import sign, verify, shared_secret
from .reasoning import Reasoner


def main() -> None:
    parser = argparse.ArgumentParser(description="Eve local research prototype")
    parser.add_argument("--state-dir", default=".eve-state")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("remember")
    add.add_argument("category", choices=["observation", "hypothesis", "validated", "failure"])
    add.add_argument("content")
    sub.add_parser("memories")
    proposal = sub.add_parser("propose")
    proposal.add_argument("kind", choices=["hypothesis", "test", "critique", "candidate_patch"])
    proposal.add_argument("problem")
    proposal.add_argument("benefit")
    intake = sub.add_parser("intake")
    intake.add_argument("file", type=Path)
    ask = sub.add_parser("ask", help="One explicitly requested model inference")
    ask.add_argument("question")
    signed = sub.add_parser("sign", help="Sign local proposal JSON, without sending")
    signed.add_argument("file", type=Path)
    receive = sub.add_parser("receive", help="Verify peer envelope and hold for review")
    receive.add_argument("file", type=Path)
    args = parser.parse_args()
    memory = Memory(args.state_dir)
    if args.command == "remember":
        output = memory.add(args.category, args.content)
    elif args.command == "memories":
        output = memory.read()
    elif args.command == "propose":
        output = make_proposal("eve", "genesis", args.kind, args.problem, args.benefit)
    elif args.command == "ask":
        output = {"answer": Reasoner().ask(args.question)}
    elif args.command == "sign":
        if args.file.stat().st_size > 32768:
            parser.error("Proposal too large")
        output = sign(json.loads(args.file.read_text(encoding="utf-8")), shared_secret())
    elif args.command == "receive":
        if args.file.stat().st_size > 40000:
            parser.error("Envelope too large")
        proposal = verify(json.loads(args.file.read_text(encoding="utf-8")), shared_secret())
        output = memory.intake(proposal)
    else:
        if args.file.stat().st_size > 32768:
            parser.error("Proposal too large")
        output = memory.intake(json.loads(args.file.read_text(encoding="utf-8")))
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
