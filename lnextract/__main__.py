import argparse
import network
import igraph

OUTPUT_FORMATS = [k for k,v in igraph.Graph._format_mapping.viewitems() if v[1] is not None]

def main():
    # arg parsing
    arg_parser = argparse.ArgumentParser(description='Network Extraction.')
    arg_parser.add_argument('tokens_file', type=argparse.FileType('r'))
    arg_parser.add_argument('book_file', type=argparse.FileType('r'))
    arg_parser.add_argument('out_format', choices=OUTPUT_FORMATS)
    arg_parser.add_argument('out_file', type=argparse.FileType('w'))
    args = arg_parser.parse_args()
    try:
        n = network.CharacterNetwork(args.tokens_file, args.book_file)
        g = n.get_igraph()
        g.write(args.out_file, format=args.out_format)
    finally:
        args.tokens_file.close()
        args.book_file.close()
        args.out_file.close()

if __name__ == '__main__':
    main()