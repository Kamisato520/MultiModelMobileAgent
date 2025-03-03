pluginManagement {
    repositories {
        maven { url = uri("https://repo.huaweicloud.com/repository/maven/") }
        maven { url = uri("https://repo.huaweicloud.com/repository/google/") }
        maven { url = uri("https://repo.huaweicloud.com/repository/gradle-plugin/") }
        maven { url = uri("https://repo.huaweicloud.com/repository/public/") }
        gradlePluginPortal()
        google()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        maven { url = uri("https://repo.huaweicloud.com/repository/maven/") }
        maven { url = uri("https://repo.huaweicloud.com/repository/google/") }
        maven { url = uri("https://repo.huaweicloud.com/repository/gradle-plugin/") }
        maven { url = uri("https://repo.huaweicloud.com/repository/public/") }
        google()
        mavenCentral()
    }
}

rootProject.name = "My Application"
include(":app")


