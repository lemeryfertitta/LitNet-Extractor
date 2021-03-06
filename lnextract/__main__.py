import argparse
from network import CharacterNetwork
import igraph
import csv

OUTPUT_FORMATS = [k for k,v in igraph.Graph._format_mapping.viewitems() if v[1] is not None]
OUTPUT_FORMATS.append('custom_edgelist')

def main():
    # arg parsing
    arg_parser = argparse.ArgumentParser(description='Network Extraction.')
    arg_parser.add_argument('tokens_file', type=argparse.FileType('r'))
    arg_parser.add_argument('book_file', type=argparse.FileType('r'))
    arg_parser.add_argument('out_format', choices=OUTPUT_FORMATS)
    arg_parser.add_argument('out_file', type=argparse.FileType('w'))
    arg_parser.add_argument('-s', '--sentiment', action='store_true')
    arg_parser.add_argument('--paragraph', dest='strategy', action='store_const', 
        const=CharacterNetwork.PARAGRAPH, default=CharacterNetwork.SENTENCE)
    arg_parser.add_argument('--sequence', dest='aggregate', action='store_false')
    args = arg_parser.parse_args()
    try:
        n = CharacterNetwork(args.tokens_file, args.book_file,
                             strategy=args.strategy, sentiment=args.sentiment,
                             aggregate=args.aggregate)
        if args.out_format == 'custom_edgelist':
            labels = n.get_vertices()['label']
            edge_df = n.get_edges()
            csv_writer = csv.writer(args.out_file)
            csv_writer.writerow(['source','target'] + list(edge_df.columns.values))
            csv_writer.writerows([labels[s], labels[t]] + list(value.values) for ((s,t),value) in edge_df.iterrows())
        else:
            g = n.get_igraph()
            g.write(args.out_file, format=args.out_format)
    finally:
        args.tokens_file.close()
        args.book_file.close()
        args.out_file.close()

if __name__ == '__main__':
    main()