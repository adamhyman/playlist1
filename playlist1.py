#  TerminusDB + Python
#  For Marie Tsaasan
#  By Adam Hyman, Michael Dang, Nathan Chau
#  Python at Orange Coast - CS231-42100

from terminusdb_client.woqlclient.woqlClient import WOQLClient
from terminusdb_client.woqlquery.woql_query import WOQLQuery as WQ

# data base information
server_url = 'https://127.0.0.1:6363'
description = 'A songs database storing information about the artist, song ' \
              'title, song length and the album'
user = 'admin'
account = 'admin'
key = 'root'
db = 'playlist'

# WOQL client
client = WOQLClient(server_url)
client.connect(user=user, account=account, key=key, db=db)


def create_schema() -> None:
    '''
    Create Schema for the playlist data base, no harm to adding repeatedly as
    it is idempotent
    :return: None
    '''

    schema = WQ().woql_and(
        WQ().doctype("scm:Song", label="Song")
            .description("A playlist that contains songs")
            .property("scm:title", "xsd:string")
            .property("scm:album", "xsd:string")
            .property("scm:artist", "xsd:string")
            .property("scm:length", "xsd:integer")

        
    )
    return schema.execute(client, "Adding Song Class to schema")


def add_song() -> None:
    '''
    User enter artist, title, length, and album name, insert into data base
    :return: None
    '''

    title = input("Enter song's title:  ")
    album = input("Enter song's album name:  ")
    artist = input("Enter artist's name:  ")
    length = int(input("Enter song's length in seconds:  "))

    # Gets number of songs
    song_query = WQ()\
        .triple("v:X", "scm:title", "v:Y")\
        .execute(client)
    number = len(song_query["bindings"])

    # Inserts new song
    WQ().woql_and(
        WQ().insert(f"doc:{number + 1}", "scm:Song")
            .property("scm:title", title)
            .property("scm:album", album)
            .property("scm:artist", artist)
            .property("scm:length", length)
    ).execute(client, f"Insert song {number} from python")


def edit_song() -> None:
    '''
    Allows user to edit a song's attributes.
    :return: None
    '''
    song_id = input("Enter song's id: ")
    song = get_song('terminusdb:///data/' + song_id)

    print('')
    print('Song ' + song_id)
    print('1.  Title:   ' + song['title'])
    print('2.  Album:   ' + song['album'])
    print('3.  Artist:  ' + song['artist'])
    print('4.  Length:  ' + str(song['length']))
    print('')

    item_to_edit = '1'
    while item_to_edit in ['1', '2', '3', '4']:

        item_to_edit = input('Enter the number of the item that you wish to edit (Enter to exit):  ')
        if item_to_edit == '':
            break

        item = ['0', 'title', 'album', 'artist', 'length'][int(item_to_edit)]

        new_value = input('Input new ' + item + ':  ')
        print ('')

        #  Because length is the only attribute of a song that is an int.  The rest are str.
        if item == 'length':
           new_value = int(new_value)

        WQ().woql_and(
            WQ().triple("doc:" + song_id, "scm:" + item, "v:Title"),
            WQ().delete_triple("doc:" + song_id, "scm:" + item, "v:Title"),
            WQ().add_triple("doc:" + song_id, "scm:" + item, new_value),
        ).execute(client, "Updated the " + str(new_value))



def print_playlist() -> None:
    '''
    Gets the playlist from database and prints it
    :return: None
    '''

    song_query = WQ()\
        .triple('v:id', 'scm:title', 'v:title')\
        .execute(client)

    print('')
    print('ID     Title                     Album                     Artist                    Length')
    print('-----------------------------------------------------------------------------------------------------')

    for song in song_query['bindings']:

        mysong = get_song(song['id'])

        print(mysong['myid'].ljust(6), mysong['title'].ljust(25), mysong['album'].ljust(25), \
              mysong['artist'].ljust(25), str(mysong['length']).ljust(23))


def get_song(item: str) -> dict:
    '''
    Gets a song from the database
    :return:  dict, with key's:  myid, title, album, artist, length
    '''
    data_query = WQ().triple(item, 'v:P', 'v:Y').execute(client)

    song = dict()

    song['myid'] = item[19:]
    for i in data_query["bindings"]:
        if i['P'] == 'terminusdb:///schema#title':
            song['title'] = i['Y']['@value']
        if i['P'] == 'terminusdb:///schema#album':
            song['album'] = i['Y']['@value']
        if i['P'] == 'terminusdb:///schema#artist':
            song['artist'] = i['Y']['@value']
        if i['P'] == 'terminusdb:///schema#length':
            song['length'] = i['Y']['@value']
    
    return song
    

def print_menu() -> None:
    '''
    prints main menu for the user
    :return: None
    '''
    print('')
    print('--------------------------')
    print('|          MENU          |')
    print('--------------------------')
    print('1.  Add song to playlist')
    print('2.  Edit song in playlist')
    print('3.  Print playlist')
    print('4.  Exit')


def main() -> None:
    """
    user can either add a song or edit a song
    :return:
    """
    create_schema()

    option = '1'
    while option in ['1', '2', '3']:
        print_menu()
        option = input("Select between 1-4:  ")
        if option == '1':
            add_song()
        elif option == '2':
            edit_song()
        elif option == '3':
            print_playlist()

    print("Thanks for using the playlist!")


if __name__ == "__main__":
    main()
