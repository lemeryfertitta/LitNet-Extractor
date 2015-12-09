import argparse
import network

def main():
    # arg parsing
    arg_parser = argparse.ArgumentParser(description='Network Extraction.')
    arg_parser.add_argument('tokens_file', type=argparse.FileType('r'))
    arg_parser.add_argument('book_file', type=argparse.FileType('r'))
    arg_parser.add_argument('vertex_file', type=argparse.FileType('w'))
    arg_parser.add_argument('edge_file', type=argparse.FileType('w'))
    args = arg_parser.parse_args()
    try:
        n = network.CharacterNetwork(args.tokens_file, args.book_file)
        n.to_csv(args.vertex_file, args.edge_file)
    finally:
        args.tokens_file.close()
        args.book_file.close()
        args.vertex_file.close()
        args.edge_file.close()

if __name__ == '__main__':
    main()