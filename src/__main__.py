from level_generation import Map


def main():
    for i in range(11):
        if i >= 1:
            map = Map(i)
            map.save(map.create())


if __name__ == "__main__":
    main()
