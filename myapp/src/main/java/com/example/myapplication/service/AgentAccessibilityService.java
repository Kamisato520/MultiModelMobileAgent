package com.example.myapplication.service;

import android.accessibilityservice.AccessibilityService;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import com.example.myapplication.agent.AgentSystem;

public class AgentAccessibilityService extends AccessibilityService {
    private AgentSystem agentSystem;

    @Override
    public void onCreate() {
        super.onCreate();
        agentSystem = new AgentSystem(this);
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event.getSource() != null) {
            AccessibilityNodeInfo rootNode = getRootInActiveWindow();
            if (rootNode != null) {
                agentSystem.processEnvironment(rootNode);
                rootNode.recycle();
            }
        }
    }

    @Override
    public void onInterrupt() {
        // 处理服务中断
    }
} 