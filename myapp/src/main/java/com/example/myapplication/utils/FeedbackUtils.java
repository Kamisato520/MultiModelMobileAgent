package com.example.myapplication.utils;

import android.content.Context;
import android.view.View;
import android.widget.Toast;

import com.google.android.material.snackbar.Snackbar;

public class FeedbackUtils {
    
    public static void showError(Context context, String message) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show();
    }
    
    public static void showSnackbar(View view, String message, String actionText, 
                                  View.OnClickListener action) {
        Snackbar.make(view, message, Snackbar.LENGTH_LONG)
                .setAction(actionText, action)
                .show();
    }
    
    public static void showLoading(Context context) {
        // 可以使用 ProgressDialog 或自定义 loading 视图
    }
    
    public static void hideLoading() {
        // 隐藏 loading
    }
} 