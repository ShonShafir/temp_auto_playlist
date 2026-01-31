import extract_artists
import check_new_releases

def main():
    #print("Extracting artist IDs...")
    #extract_artists.extract_artist_ids()
    print("Checking for new releases...")
    check_new_releases.check_new_releases()
    print("Done!")

if __name__ == '__main__':
    main()
