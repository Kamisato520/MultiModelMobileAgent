package com.example.myapplication.model;

public class FunctionModule {
    private int iconResId;
    private String name;
    private String description;
    private int backgroundColor;
    private Class<?> targetActivity;

    public FunctionModule(int iconResId, String name, String description, int backgroundColor, Class<?> targetActivity) {
        this.iconResId = iconResId;
        this.name = name;
        this.description = description;
        this.backgroundColor = backgroundColor;
        this.targetActivity = targetActivity;
    }

    public int getIconResId() {
        return iconResId;
    }

    public String getName() {
        return name;
    }

    public String getDescription() {
        return description;
    }

    public int getBackgroundColor() {
        return backgroundColor;
    }

    public Class<?> getTargetActivity() {
        return targetActivity;
    }
} 