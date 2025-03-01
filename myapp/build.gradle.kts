// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    id("com.android.application") version "8.5.1" apply false
    id("org.jetbrains.kotlin.android") version "1.9.0" apply false
}

// 添加全局配置
buildscript {
    repositories {
        maven { url = uri("https://repo.huaweicloud.com/repository/maven/") }
        maven { url = uri("https://repo.huaweicloud.com/repository/google/") }
        maven { url = uri("https://repo.huaweicloud.com/repository/gradle-plugin/") }
        google()
        mavenCentral()
    }
}

// 如果需要，可以在这里添加其他全局配置
