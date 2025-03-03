package com.example.myapplication.agent;

import android.content.Context;
import android.view.accessibility.AccessibilityNodeInfo;

public class AgentSystem {
    private final EnvironmentPerception perception;
    private final DecisionEngine decisionMaker;
    private final ActionExecutor executor;
    private final LearningModule learningModule;

    public AgentSystem(Context context) {
        this.perception = new EnvironmentPerception(context);
        this.decisionMaker = new DecisionEngine();
        this.executor = new ActionExecutor(context);
        this.learningModule = new LearningModule();
    }

    public void processEnvironment(AccessibilityNodeInfo rootNode) {
        // 感知环境
        UIState currentState = perception.analyzeUI(rootNode);
        // 决策
        Action nextAction = decisionMaker.decide(currentState);
        // 执行
        boolean success = executor.executeAction(nextAction);
        // 学习
        learningModule.learn(currentState, nextAction, success);
    }
} 