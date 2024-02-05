
import os


def sumresult():
    '''
    Will sum up the output from the tests and put the result in
    'Total.md'
    '''

    filename = "Total.md"
    points = 0
    total = 0
    with open("result", "r") as res:
        for scores in res.readlines():
            score, max = scores.split("/")
            points += int(score)
            total += int(max)

    os.remove(os.getcwd()+"/result")
    with open(filename, "w") as score:
        score.write("# Result:\n")
        score.write(f"{points} out of {total}")


if __name__ == "__main__":
    sumresult()
    print("Done writing test result")
