#pip install PyGithub

from github import Github, Auth
from github.GithubException import RateLimitExceededException, GithubException
import time

GITHUB_TOKEN = "YOUR_PERSONAL_ACCESS_TOKEN"  # Replace with your GitHub Personal Access Token
# YOUR_GITHUB_USERNAME = "your_username" # Not strictly needed if using token for self


def get_all_followers(user_obj):
    print("Fetching followers...")
    followers = set()
    try:
        for follower in user_obj.get_followers():
            followers.add(follower.login)
        print(f"Found {len(followers)} followers.")
    except RateLimitExceededException:
        print("Rate limit exceeded while fetching followers.")
        return None
    except GithubException as e:
        print(f"GitHub API error while fetching followers: {e.data.get('message', str(e))}")
        return None
    return followers

def get_all_following(user_obj):
    print("Fetching users you are following...")
    following = set()
    try:
        for followed_user in user_obj.get_following():
            following.add(followed_user.login)
        print(f"You are following {len(following)} users.")
    except RateLimitExceededException:
        print("Rate limit exceeded while fetching following list.")
        return None
    except GithubException as e:
        print(f"GitHub API error while fetching following list: {e.data.get('message', str(e))}")
        return None
    return following

def unfollow_users_on_github(github_instance, users_to_unfollow_logins):
    if not users_to_unfollow_logins:
        print("No users to unfollow.")
        return

    print("\nStarting unfollow process...")
    unfollowed_count = 0
    failed_to_unfollow = []
    current_user = github_instance.get_user()

    for username_to_unfollow in users_to_unfollow_logins:
        if username_to_unfollow == current_user.login:
            print(f"Skipping attempt to unfollow yourself ({username_to_unfollow}).")
            continue
        try:
            user_to_unfollow_obj = github_instance.get_user(username_to_unfollow)
            current_user.remove_from_following(user_to_unfollow_obj)
            print(f"Successfully unfollowed {username_to_unfollow}.")
            unfollowed_count += 1
            time.sleep(1) # API delay
        except RateLimitExceededException:
            print(f"Rate limit exceeded. Could not unfollow {username_to_unfollow} and subsequent users.")
            failed_to_unfollow.append(username_to_unfollow)
            break
        except GithubException as e:
            print(f"GitHub API error unfollowing {username_to_unfollow}: {e.data.get('message', str(e))}")
            failed_to_unfollow.append(username_to_unfollow)
        except Exception as e:
            print(f"Unexpected error unfollowing {username_to_unfollow}: {str(e)}")
            failed_to_unfollow.append(username_to_unfollow)

    print("\nUnfollow process finished.")
    print(f"Successfully unfollowed {unfollowed_count} user(s).")
    if failed_to_unfollow:
        print(f"Failed to unfollow {len(failed_to_unfollow)} user(s): {failed_to_unfollow}")


def main():
    if not GITHUB_TOKEN or GITHUB_TOKEN == "YOUR_PERSONAL_ACCESS_TOKEN":
        print("Error: Please set your GITHUB_TOKEN in the script.")
        return

    try:
        auth = Auth.Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        authenticated_user = g.get_user() 
        print(f"Successfully authenticated as {authenticated_user.login}")
    except RateLimitExceededException:
        print("GitHub API rate limit exceeded during authentication. Please wait and try again later.")
        return
    except GithubException as e:
        print(f"An error occurred during authentication: {e.data.get('message', str(e))}")
        return
    except Exception as e:
        print(f"An unexpected error occurred during setup: {str(e)}")
        return

    my_followers = get_all_followers(authenticated_user)
    my_following = get_all_following(authenticated_user)

    if my_followers is None or my_following is None:
        print("Could not retrieve follower/following lists due to previous errors. Exiting.")
        return

    users_to_unfollow = my_following - my_followers
    print(f"\nFound {len(users_to_unfollow)} user(s) you are following who are not following you back.")

    if users_to_unfollow:
        print("These users are:", ", ".join(users_to_unfollow) if users_to_unfollow else "None")
        confirm_unfollow_all = input(f"\nAre you sure you want to unfollow all {len(users_to_unfollow)} users listed? (yes/no): ")
        if confirm_unfollow_all.lower() == 'yes':
            unfollow_users_on_github(g, users_to_unfollow)
        else:
            print("Unfollow process aborted by user.")
    else:
        print("No users to unfollow. Your following list is aligned with your followers!")

if __name__ == "__main__":
    main()
