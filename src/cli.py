from agent import respond


def main() -> None:
    while True:
        try:
            message = input("Aster & Row Support > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if message.strip().lower() in {"exit", "quit"}:
            break
        response = respond(message)
        print(response)
        if "[Source:" in response:
            print("Sources: " + " | ".join("[Source:" + part.split("]", 1)[0] + "]" for part in response.split("[Source:")[1:] if "]" in part))
        if "support team" in response.lower() or "contact" in response.lower():
            print("[Human handoff recommended]")


if __name__ == "__main__":
    main()