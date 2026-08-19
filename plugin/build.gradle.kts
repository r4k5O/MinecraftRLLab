plugins {
    java
}

repositories {
    mavenCentral()
    maven {
        name = "papermc"
        url = uri("https://repo.papermc.io/repository/maven-public/")
    }
}

java {
    toolchain.languageVersion.set(JavaLanguageVersion.of(25))
}

val offlinePaperLibs = rootProject.file("toolchain/paper-libs")
val gradleLibs = gradle.gradleHomeDir!!.resolve("lib")
val supplemental = fileTree(gradleLibs) {
    include("annotations-*.jar", "guava-*.jar", "gson-*.jar", "jspecify-*.jar", "commons-lang3-*.jar", "fastutil-*.jar")
}

if (offlinePaperLibs.exists()) {
    dependencies {
        compileOnly(fileTree(offlinePaperLibs) { include("**/*.jar") })
        compileOnly(supplemental)
        testImplementation(fileTree(offlinePaperLibs) { include("**/*.jar") })
        testImplementation(supplemental)
    }
} else {
    dependencies {
        compileOnly("io.papermc.paper:paper-api:26.2.build.+")
        testImplementation("io.papermc.paper:paper-api:26.2.build.+")
    }
}

tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
    options.release.set(25)
}

tasks.jar {
    archiveBaseName.set("MinecraftRLLab-Plugin")
    archiveVersion.set(project.version.toString())
}

val runTests = tasks.register<JavaExec>("runTests") {
    group = "verification"
    description = "Runs the dependency-free Java test suite."
    dependsOn(tasks.testClasses)
    classpath = sourceSets.test.get().runtimeClasspath
    mainClass.set("dev.r4k5o.minecraftrl.TestSuite")
}

tasks.test { enabled = false }
tasks.check { dependsOn(runTests) }
