import argparse
import itertools
import json
from collections import namedtuple

import requests
from jinja2 import Template

USERNAME = "GCBallesteros"

PremierRepo = namedtuple(
    "PremierRepo", ["owner", "name", "description", "category", "stars", "lang"]
)

Repo = namedtuple("Repo", ["owner", "name", "full_name", "stars"])

with open("./premier_repos.json", "r") as fh:
    premiered_repositories = json.load(fh)


def make_img_tag(src: str) -> str:
    return f'<img src="{src}" height="18" style="vertical-align: middle;">'


badges = {
    "lua": make_img_tag(
        "https://img.shields.io/badge/lua-%232C2D72.svg?style=for-the-badge&logo=lua&logoColor=white"
    ),
    "c": make_img_tag(
        "https://img.shields.io/badge/c-%2300599C.svg?style=for-the-badge&logo=c&logoColor=white"
    ),
    "rust": make_img_tag(
        "https://img.shields.io/badge/rust-%23000000.svg?style=for-the-badge&logo=rust&logoColor=white"
    ),
    "python": make_img_tag(
        "https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"
    ),
    "vim": make_img_tag(
        "https://img.shields.io/badge/VIM-%2311AB00.svg?style=for-the-badge&logo=vim&logoColor=white"
    ),
}


def get_star_count_for_user_repositories(owner: str, token: str) -> list[Repo]:
    endpoint = f"https://api.github.com/users/{owner}/repos"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    repos = []

    # Keep making requests until all pages have been retrieved
    page = 1
    while True:
        params = {"page": page}
        response = requests.get(endpoint, headers=headers, params=params)

        if response.status_code == 200:
            repositories_page = response.json()

            if not repositories_page:
                break

            repos.extend(
                [
                    Repo(
                        repo["owner"]["login"],
                        repo["name"],
                        repo["full_name"],
                        repo["stargazers_count"],
                    )
                    for repo in repositories_page
                ]
            )

            # Move to the next page
            page += 1
        else:
            # Handle errors
            print(f"Error getting repository list: {response.status_code}")
            break

    return repos


def prepare_displayed_categories(
    repositories: list[Repo], category: str
) -> list[PremierRepo]:
    return [
        PremierRepo(
            x.owner,
            x.name,
            premiered_repositories[x.full_name]["description"],
            premiered_repositories[x.full_name]["category"],
            x.stars,
            premiered_repositories[x.full_name]["lang"],
        )
        for x in [
            repo for repo in repositories if repo.full_name in premiered_repositories
        ]
        if premiered_repositories[x.full_name]["category"] == category
        and premiered_repositories[x.full_name]["display"]
    ]


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", help="Authentication token")

    return parser.parse_args()


def get_token():
    """First check the command line and if that is not passed look for in ./.TOKEN

    .TOKEN should not be committed! It's just to help during local dev.
    """
    args = parse_arguments()

    if args.token:
        return args.token

    # If not provided, try to get it from the .TOKEN file
    try:
        with open(".TOKEN", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Authentication token not provided.")
        exit(1)


if __name__ == "__main__":
    gh_token = get_token()
    all_repos = list(
        itertools.chain.from_iterable(
            [
                get_star_count_for_user_repositories(owner, gh_token)
                for owner in ["GCBallesteros", "QuantumPhotonicsLab"]
            ]
        )
    )

    total_stars = sum(
        [
            repo.stars
            for repo in all_repos
            if (repo.owner == "GCBallesteros" or repo.name == "readPTU")
        ]
    )

    vim_repositories = prepare_displayed_categories(all_repos, "vim")
    scientific_repositories = prepare_displayed_categories(all_repos, "scientific")

    with open("./README.template.md", "r") as fh:
        template = Template(fh.read())
        output = template.render(
            total_stars=total_stars,
            science_stars=sum([repo.stars for repo in scientific_repositories]),
            vim_stars=sum([repo.stars for repo in vim_repositories]),
            vim_repos=sorted(vim_repositories, key=lambda x: x.stars, reverse=True),
            science_repos=sorted(
                scientific_repositories, key=lambda x: x.stars, reverse=True
            ),
            badges=badges,
        )

    print(output)
