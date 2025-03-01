package com.example.myapplication.agent;

import android.content.Context;
import android.view.accessibility.AccessibilityNodeInfo;
import java.util.ArrayList;
import java.util.List;

public class EnvironmentPerception {
    private final Context context;

    public EnvironmentPerception(Context context) {
        this.context = context;
    }

    public UIState analyzeUI(AccessibilityNodeInfo rootNode) {
        List<UIElement> elements = new ArrayList<>();
        extractUIElements(rootNode, elements);
        return new UIState(elements);
    }

    private void extractUIElements(AccessibilityNodeInfo node, List<UIElement> elements) {
        if (node == null) return;

        // 提取当前节点信息
        if (node.isClickable() || node.isEditable()) {
            elements.add(new UIElement(
                node.getViewIdResourceName(),
                node.getText() != null ? node.getText().toString() : "",
                node.getClassName().toString(),
                node.getBoundsInScreen()
            ));
        }

        // 递归处理子节点
        for (int i = 0; i < node.getChildCount(); i++) {
            extractUIElements(node.getChild(i), elements);
        }
    }
} 