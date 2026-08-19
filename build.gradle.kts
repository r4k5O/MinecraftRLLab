allprojects {
    group = "dev.r4k5o"
    version = providers.gradleProperty("mcrlVersion").orElse("0.3.0-dev").get()
}
