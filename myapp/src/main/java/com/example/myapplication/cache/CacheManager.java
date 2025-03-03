package com.example.myapplication.cache;

import android.content.Context;
import android.content.SharedPreferences;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;

public class CacheManager {
    private static final String PREF_NAME = "app_cache";
    private static final String KEY_SEARCH_HISTORY = "search_history";
    private static final String KEY_QUICK_COMMANDS = "quick_commands";
    private static final int MAX_HISTORY_SIZE = 10;
    
    private SharedPreferences preferences;
    private Gson gson;
    
    public CacheManager(Context context) {
        preferences = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        gson = new Gson();
    }
    
    public void saveSearchHistory(String query) {
        List<String> history = getSearchHistory();
        if (!history.contains(query)) {
            history.add(0, query);
            if (history.size() > MAX_HISTORY_SIZE) {
                history = history.subList(0, MAX_HISTORY_SIZE);
            }
            preferences.edit()
                    .putString(KEY_SEARCH_HISTORY, gson.toJson(history))
                    .apply();
        }
    }
    
    public List<String> getSearchHistory() {
        String json = preferences.getString(KEY_SEARCH_HISTORY, null);
        if (json == null) {
            return new ArrayList<>();
        }
        Type type = new TypeToken<List<String>>(){}.getType();
        return gson.fromJson(json, type);
    }
    
    public void clearSearchHistory() {
        preferences.edit().remove(KEY_SEARCH_HISTORY).apply();
    }
    
    public void saveQuickCommands(List<String> commands) {
        preferences.edit()
                .putString(KEY_QUICK_COMMANDS, gson.toJson(commands))
                .apply();
    }
    
    public List<String> getQuickCommands() {
        String json = preferences.getString(KEY_QUICK_COMMANDS, null);
        if (json == null) {
            return getDefaultQuickCommands();
        }
        Type type = new TypeToken<List<String>>(){}.getType();
        return gson.fromJson(json, type);
    }
    
    private List<String> getDefaultQuickCommands() {
        List<String> commands = new ArrayList<>();
        commands.add("查快递");
        commands.add("找网点");
        commands.add("寄包裹");
        commands.add("邮编查询");
        commands.add("投诉建议");
        return commands;
    }
} 