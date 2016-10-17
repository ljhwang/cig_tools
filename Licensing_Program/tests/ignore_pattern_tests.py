patterns = [
    "one/**/*",
    "one/**/two/*",
    "**/two/*",
    "**/*",
]

tests = [
    "one/zero.txt",
    "one/two/zero.txt",
    "one/nan/two/zero.txt",
    "one/two/nan/zero.txt",
    "two/one/zero.txt",
    "one/nan/zero.txt",
    "nan/two/zero.txt",
    "two/zero.txt",
    "zero.txt",
]
