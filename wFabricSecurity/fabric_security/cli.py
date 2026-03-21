#!/usr/bin/env python3
"""
wFabricSecurity CLI

Command-line interface for wFabricSecurity operations.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("FabricCLI")


def cmd_register(security, args):
    """Register identity and code."""
    print("Registering identity...")
    result = security.register_identity()
    print(f"Identity registered: {result}")

    if args.code_paths:
        print(f"Registering code from: {args.code_paths}")
        paths = args.code_paths.split(",")
        result = security.register_code(paths, args.version)
        print(f"Code registered: {result}")
    else:
        print("No code paths specified, skipping code registration")


def cmd_verify(security, args):
    """Verify code integrity."""
    if args.code_paths:
        paths = args.code_paths.split(",")
        print(f"Verifying code: {paths}")
        result = security.verify_code(paths)
        print(f"Verification result: {result}")
    else:
        print("Verifying own code...")
        result = security.verify_code()
        print(f"Verification result: {result}")


def cmd_send(security, args):
    """Send a message to another participant."""
    from .core.enums import DataType

    data_type = DataType.JSON
    if args.type:
        data_type = DataType(args.type)

    content = args.content
    if args.file:
        with open(args.file) as f:
            content = f.read()

    print(f"Sending message to {args.recipient}...")
    message = security.create_message(
        sender=security.get_signer_id(),
        recipient=args.recipient,
        content=content,
        data_type=data_type,
    )
    print(f"Message created: {message.message_id}")
    print(f"Content hash: {message.content_hash}")
    print(f"Signature: {message.signature[:50]}...")


def cmd_receive(security, args):
    """Receive and verify messages."""
    messages = security.get_messages_for_recipient(args.identity)
    print(f"Found {len(messages)} messages for {args.identity}")

    for msg in messages:
        print(f"\n--- Message {msg.message_id} ---")
        print(f"From: {msg.sender}")
        print(f"Timestamp: {msg.timestamp}")
        print(f"Type: {msg.data_type}")

        try:
            security.verify_message(msg)
            print("Signature: VALID")
        except Exception as e:
            print(f"Signature: INVALID - {e}")

        if args.show_content:
            print(f"Content: {msg.content[:200]}...")


def cmd_permissions(security, args):
    """Manage communication permissions."""
    if args.action == "list":
        allowed = security.get_allowed_communications(args.identity)
        print(f"Allowed communications for {args.identity}:")
        for target in allowed:
            print(f"  - {target}")

    elif args.action == "add":
        security.register_communication(args.identity, args.target)
        print(f"Added permission: {args.identity} -> {args.target}")

    elif args.action == "remove":
        print("Remove permission not implemented yet")

    elif args.action == "check":
        can_comm = security.can_communicate_with(args.identity, args.target)
        print(f"Can {args.identity} communicate with {args.target}: {can_comm}")


def cmd_revoke(security, args):
    """Revoke a participant."""
    print(f"Revoking participant: {args.participant_id}")
    result = security.revoke_participant(args.participant_id)
    print(f"Revocation result: {result}")


def cmd_stats(security, args):
    """Show statistics."""
    stats = security.get_stats()
    print("\n=== wFabricSecurity Statistics ===")
    for key, value in stats.items():
        print(f"{key}: {value}")


def cmd_info(security, args):
    """Show identity information."""
    print("\n=== Identity Information ===")
    print(f"Identity: {security.get_signer_id()}")
    print(f"Common Name: {security.get_signer_cn()}")
    print(f"Using Fabric: {security.is_using_fabric}")
    print(f"Code Hash: {security.compute_code_hash([__file__])}")


def main():
    parser = argparse.ArgumentParser(
        description="wFabricSecurity CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--config",
        "-c",
        help="Configuration file path",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    register_parser = subparsers.add_parser(
        "register", help="Register identity and code"
    )
    register_parser.add_argument("--code-paths", help="Comma-separated code paths")
    register_parser.add_argument("--version", default="1.0.0", help="Code version")

    verify_parser = subparsers.add_parser("verify", help="Verify code integrity")
    verify_parser.add_argument("--code-paths", help="Comma-separated code paths")

    send_parser = subparsers.add_parser("send", help="Send a message")
    send_parser.add_argument("recipient", help="Recipient identity")
    send_parser.add_argument("--content", "-m", help="Message content")
    send_parser.add_argument("--file", "-f", help="File containing message content")
    send_parser.add_argument("--type", "-t", choices=["json", "image", "p2p", "binary"])

    receive_parser = subparsers.add_parser("receive", help="Receive messages")
    receive_parser.add_argument("identity", help="Recipient identity")
    receive_parser.add_argument("--show-content", action="store_true")

    perm_parser = subparsers.add_parser("permissions", help="Manage permissions")
    perm_parser.add_argument("action", choices=["list", "add", "remove", "check"])
    perm_parser.add_argument("identity", help="Source identity")
    perm_parser.add_argument("--target", help="Target identity")

    revoke_parser = subparsers.add_parser("revoke", help="Revoke a participant")
    revoke_parser.add_argument("participant_id", help="Participant to revoke")

    subparsers.add_parser("stats", help="Show statistics")
    subparsers.add_parser("info", help="Show identity information")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    from .fabric_security import FabricSecuritySimple

    security = FabricSecuritySimple(
        args.identity if "identity" in args else "Admin@org1.net"
    )

    commands = {
        "register": cmd_register,
        "verify": cmd_verify,
        "send": cmd_send,
        "receive": cmd_receive,
        "permissions": cmd_permissions,
        "revoke": cmd_revoke,
        "stats": cmd_stats,
        "info": cmd_info,
    }

    if args.command in commands:
        commands[args.command](security, args)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
