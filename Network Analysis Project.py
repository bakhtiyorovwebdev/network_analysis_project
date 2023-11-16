"""
COMP1811 Python Project
Corresponds to a network of members and their connections which can be loaded from a file,
and then the user can interact with the network to find connections, friends of friends and more.
"""
# Import the Union type from typing to allow a function to return different types
from typing import Union


class Member:
    """
    A class to represent a member Generic member class
    """

    def __init__(self, name: str) -> None:
        """
        Constructor for the Member class
        :param name: The name of the member
        """
        # Private instance variables
        self.__name: str = name

    def __str__(self) -> str:
        """
        Returns a string representation of the member
        :return:
        """
        return self.__name

    def get_name(self) -> str:
        """
        Gets the name of the member
        :return:
        """
        return self.__name


class NetworkMember(Member):
    """
    A class to represent a member of a network
    """

    def __init__(self, name: str) -> None:
        """
        Constructor for the NetworkMember class
        :param name: The name of the member
        """
        # Call the super class constructor
        super().__init__(name)
        # Private instance variables
        # A set of the member's friends
        self.__friends: set['NetworkMember'] = set()

    def __repr__(self) -> str:
        """
        Returns a string representation of the member, used to show his connections
        :return: String representation of the member
        """
        # Get the names of the member's friends and join them into a string
        friends_str = ', '.join([friend.get_name() for friend in self.__friends])
        # If the member has no friends, set the string to 'None'
        if len(self.__friends) == 0:
            friends_str = 'None'
        # Return the string representation of the member with his friends
        return f"{self.get_name()} -> {friends_str}"

    def get_friends(self) -> set['NetworkMember']:
        """
        Gets the member's friends
        :return: The member's friends
        """
        return self.__friends

    def mutual_friends(self, member: 'NetworkMember') -> set['NetworkMember']:
        """
        Gets the mutual friends between the member and another member
        :param member: The other member
        :return: The mutual friends
        """
        # Find the mutual friends as the intersection of the member's friends and the other member's friends sets
        return self.__friends.intersection(member.get_friends())

    def count_mutual_friends(self, member: 'NetworkMember') -> int:
        """
        Counts the number of mutual friends between the member and another member
        :param member: The other member
        :return:
        """
        return len(self.mutual_friends(member))

    def number_of_friends(self) -> int:
        """
        Counts the number of friends the member has
        :return: Number of friends
        """
        return len(self.__friends)


class Network:
    """
    A class to represent a network of members and their connections
    """

    def __init__(self) -> None:
        """
        Constructor for the Network class
        """
        # Private instance variables
        # A dictionary of the members in the network, with the member's name as the key
        self.__members: dict[str, NetworkMember] = {}

    def add_member(self, name: str) -> NetworkMember:
        """
        Adds a member to the network
        :param name: The name of the member
        :return:
        """
        # If the member is not in the network, add them
        if name not in self.__members:
            self.__members[name] = NetworkMember(name)
        # Return the member
        return self.__members[name]

    def make_friends(self, member1: NetworkMember, member2: NetworkMember) -> None:
        """
        Makes two network members friends
        :param member1: First member
        :param member2: Second member
        :return: None
        """
        # Add the members to each other's friends sets
        member1.get_friends().add(member2)
        member2.get_friends().add(member1)

    def from_file(self, filename: str) -> bool:
        """
        Loads a network from a file
        :param filename: The name of the file
        :return: True if the network was loaded successfully, False otherwise
        """
        # Clear the network
        self.__members = {}
        # Try to open the file, and return False if it doesn't exist
        try:
            with open(filename) as file:
                file_lines = file.readlines()
        except FileNotFoundError:
            return False

        members_count = None
        # Loop through the lines in the file
        for i, line in enumerate(file_lines):
            # Strip the line of line breaks
            line = line.strip()
            # For the first line, try to convert it to an integer and return False if it can't be converted
            if i == 0:

                try:
                    # Set the number of members in the network
                    members_count = int(file_lines[0])
                except ValueError:
                    return False
            # For the rest of the lines
            else:
                # Split the line into the names of the members
                member_names = line.split()
                # If there is 1 or 2 member names, add them to the network
                if len(member_names) <= 2:
                    # Add the first member to the network
                    member1 = self.add_member(member_names[0].strip())
                    # If there are 2 members, add them to the network and make them friends
                    if len(member_names) > 1:
                        # Add the second member to the network
                        member2 = self.add_member(member_names[1].strip())
                        # Make the members friends
                        self.make_friends(member1, member2)
                # If there are more than 2 member names, return False as it's an invalid file
                else:
                    return False
        # If the number of members in the network doesn't match the number of members in the file, return False
        if len(self.get_members()) != members_count:
            return False
        # Return True if the network was loaded successfully
        return True

    def count_mutual_friends(self, member: NetworkMember) -> dict[NetworkMember, int]:
        """
        Counts the number of mutual friends between the member and all other members in the network
        :param member: The member
        :return: A dictionary of the other members and the number of mutual friends
        """
        # Dictionary to store the number of mutual friends between the member and the other members
        mutual_friends = {}
        # Loop through the members in the network
        for second_member in self.__members.values():
            # Save the number of mutual friends between the member and the other member in the dictionary
            mutual_friends[second_member] = member.count_mutual_friends(second_member)
        # Return the dictionary
        return mutual_friends

    def recommended_friend(self, member: NetworkMember) -> Union[NetworkMember, None]:
        """
        Finds the recommended friend for the member
        :param member: The member
        :return: The recommended friend, or None if there is no recommended friend
        """
        # Get the number of mutual friends between the member and all other members
        mutual_friend_dict = self.count_mutual_friends(member)
        # Sort the mutual friends by the number of mutual friends
        ordered_mutual_friends = sorted(mutual_friend_dict.items(),
                                        key=lambda friend_info: friend_info[1], reverse=True)

        # Find the recommended friend
        # Start with the member with the most mutual friends
        recommended_friend, common_friends_count = ordered_mutual_friends[0]
        # While the recommended friend is the member, or the recommended friend is already a friend of the member,
        # remove the recommended friend from the list and try the next recommended friend
        while recommended_friend == member or recommended_friend in member.get_friends():
            # Remove the recommended friend from the list
            ordered_mutual_friends.pop(0)
            # If there are no more friends, return None
            if len(ordered_mutual_friends) == 0:
                break
            # Get the next recommended friend
            recommended_friend, common_friends_count = ordered_mutual_friends[0]
        # If the recommended friend has no friends in common with the member or the recommended friend is the member,
        # return None
        if common_friends_count == 0 or recommended_friend == member:
            return None
        # Return the recommended friend
        return recommended_friend

    def get_member(self, member_name: str) -> Union[NetworkMember, None]:
        """
        Gets a member from the network by name if they are in the network, otherwise returns None
        :param member_name:
        :return: The member, or None if the member is not in the network
        """
        if member_name in self.__members:
            return self.__members[member_name]
        return None

    def get_members(self) -> list[NetworkMember]:
        """
        Gets a list of all the members in the network
        :return: A list of all the members in the network
        """
        return list(self.__members.values())


class InteractiveNetwork(Network):
    """
    An interactive version of the Network class
    """

    def display(self) -> None:
        """
        Displays the network
        :return:
        """
        # Loop through the members in the network and prints their representation (name and friends)
        for member in self.__members.values():
            print(repr(member))

    def recommend_a_friend(self) -> None:
        """
        Recommends a friend for a member asking for input from the user
        :return:
        """
        # Get the name of the member and get the member from the network
        member_name = input("Enter a member name: ")
        member = self.get_member(member_name)
        # If the member is not in the network, print an error message and return
        if not member:
            print(f"Member {member_name} not found")
            return
        # Get the recommended friend for the member
        friend = self.recommended_friend(member)
        print(f"The recommended friend for {member} is {friend}")

    def number_of_friends(self) -> None:
        """
        Prints the number of friends for a member asking for input from the user
        :return:
        """
        # Get the name of the member and get the member from the network
        member_name = input("Enter a member name: ")
        member = self.get_member(member_name)
        # If the member is not in the network, print an error message and return
        if not member:
            print(f"  Member {member_name} not found")
            return
        # Get the number of friends for the member
        number_of_friends = member.number_of_friends()
        print(f"Member {member} has {number_of_friends} friends")

    def least_friends(self) -> None:
        """
        Prints the member names for the member with the least friends and the members with 0 friends
        :return: None
        """
        # Sort the members by the number of friends
        ordered_members = sorted(self.get_members(),
                                 key=NetworkMember.number_of_friends)
        # List to store the members with 0 friends and the members with the least friends
        no_friends = []
        least_friends = []
        # Loop through the ordered members
        for member in ordered_members:
            # If the member has 0 friends, add the member to the list of members with 0 friends
            if member.number_of_friends() == 0:
                no_friends.append(member)
            # If the list of members with the least friends is empty, add the member to the list of members with the least
            elif len(least_friends) == 0:
                least_friends.append(member)
            # If the member has the same number of friends as the members in the list of members with the least friends,
            # add the member to the list of members with the least friends
            elif member.number_of_friends() == least_friends[0].number_of_friends():
                least_friends.append(member)
            # If the member has more friends than the members in the list of members with the least friends,
            # end the loop
            else:
                break
        # Build a string of the member names for the members with the least friends and zero friends and print them
        least_friends_str = ', '.join([str(member) for member in least_friends])
        print(f"The member name for the member with least friends is: {least_friends_str}")

        no_friends_str = ', '.join([str(member) for member in no_friends])
        print(f"The member name for the member with 0 friends is: {no_friends_str}")

    def indirect_friends(self) -> None:
        """
        Prints the indirect friends (friends of friends) for a member asking for input from the user
        :return: None
        """
        # Get the name of the member and get the member from the network
        member_name = input("Enter a member name: ")
        member = self.get_member(member_name)
        # If the member is not in the network, print an error message and return
        if not member:
            print(f"  Member {member_name} not found")
            return
        # For each friend of the member, print the friend's name and friends
        for friend in member.get_friends():
            print(repr(friend))


def menu() -> None:
    """
    Displays the menu and handles the user's choice until the user chooses to quit
    :return: None
    """
    # Loop until the user chooses to quit
    while True:
        # Print the menu
        print("""
Main menu:
 1. Display the social network
 2. Recommend a friend for a member
 3. Display the number of friends for a member
 4. Display members with the least number of or have 0 friends
 5. Display friends of friends for a member
 6. Change social network data file
 7. Quit
        """)
        # Get the user's selection
        selection = input("Choose an option: ")

        if selection == "1":
            # Display the network
            social_NW.display()
        elif selection == "2":
            # Recommend a friend for a member
            social_NW.recommend_a_friend()
        elif selection == "3":
            # Display the number of friends for a member
            social_NW.number_of_friends()
        elif selection == "4":
            # Display members with the least number of or have 0 friends
            social_NW.least_friends()
        elif selection == "5":
            # Display friends of friends for a member
            social_NW.indirect_friends()
        elif selection == "6":
            # Exit the loop to change the network data file
            break
        elif selection == "7":
            # Exit the loop to quit the program
            quit()
        else:
            # Print an error message if the user's selection is invalid
            print("Invalid choice, try again!")


# Create a new network
social_NW = InteractiveNetwork()

# Loop until the user chooses to quit
while True:
    # Get the network data filename from the user
    network_data_filename = input('Enter a filename for network data: ')
    if network_data_filename != "n":
        # Load the network data from the file
        valid_file = social_NW.from_file(network_data_filename)
    # If the user enters 'n', exit the loop to quit the program
    else:
        running = False
        break
    # If the network data file is invalid, print an error message
    if not valid_file:
        print(f"The network is inconsistent, try another file.")
    # If the network data file is valid, display the menu
    else:
        menu()
