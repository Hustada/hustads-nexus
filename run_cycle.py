import os

from supervisor import run_research_cycle


def main():
    print("Starting the research cycle...")
    goal = input("Enter a research goal: ")
    print("Running research cycle, please wait...")
    result = run_research_cycle(goal)
    print("\nResearch cycle result:\n")
    print(result)


if __name__ == "__main__":
    main()
