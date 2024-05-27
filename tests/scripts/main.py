import uvicorn
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, help="Host to listen on", 
                        default="0.0.0.0")
    parser.add_argument("--port", type=int, help="Port to listen on",
                        default=8081)
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    return parser.parse_args()


def main():
    args = parse_args()
    uvicorn.run("src.start:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()