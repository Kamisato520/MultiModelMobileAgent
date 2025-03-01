package com.example.myapplication;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.speech.RecognitionListener;
import android.speech.SpeechRecognizer;
import android.view.Menu;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.google.android.material.chip.Chip;
import com.google.android.material.chip.ChipGroup;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.List;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import com.example.myapplication.utils.FeedbackUtils;
import com.example.myapplication.cache.CacheManager;
import com.example.myapplication.utils.CustomAnimationUtils;
import android.speech.RecognizerIntent;

import com.example.myapplication.model.FunctionModule;
import com.example.myapplication.adapter.FunctionModuleAdapter;
import com.example.myapplication.agent.AgentSystem;

public class MainActivity extends AppCompatActivity {

    private EditText inputText;
    private FloatingActionButton voiceInputFab;
    private TextView displayArea;
    private TextView welcomeTextView;
    private RecyclerView functionModulesView;
    private ChipGroup quickCommandsGroup;
    private static final int PERMISSION_REQUEST_CODE = 1000;
    private SpeechRecognizer speechRecognizer;
    private CacheManager cacheManager;
    private AgentSystem agentSystem;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        cacheManager = new CacheManager(this);

        // Initialize Toolbar
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setHomeAsUpIndicator(R.drawable.ic_menu);

        // Initialize UI components
        initializeViews();
        setupWelcomeMessage();
        setupFunctionModules();
        setupQuickCommands();
        setupVoiceInput();
        checkPermissions();
        initializeSpeechRecognizer();

        // 初始化代理系统
        agentSystem = new AgentSystem(this);
        
        // 设置可访问性服务
        if (!isAccessibilityServiceEnabled()) {
            requestAccessibilityPermission();
        }

        // 添加进入动画
        CustomAnimationUtils.fadeIn(welcomeTextView);
        CustomAnimationUtils.scaleIn(functionModulesView);
    }

    private void initializeViews() {
        inputText = findViewById(R.id.inputText);
        voiceInputFab = findViewById(R.id.voice_input_fab);
        displayArea = findViewById(R.id.displayArea);
        welcomeTextView = findViewById(R.id.welcome_text);
        functionModulesView = findViewById(R.id.function_modules);
        quickCommandsGroup = findViewById(R.id.quick_commands_group);
    }

    private void setupWelcomeMessage() {
        Calendar calendar = Calendar.getInstance();
        int hour = calendar.get(Calendar.HOUR_OF_DAY);
        String greeting;
        
        if (hour >= 0 && hour < 6) {
            greeting = "凌晨好呀，邮小助为您服务！";
        } else if (hour >= 6 && hour < 12) {
            greeting = "上午好呀，邮小助为您服务！";
        } else if (hour >= 12 && hour < 18) {
            greeting = "下午好呀，邮小助为您服务！";
        } else {
            greeting = "晚上好呀，邮小助为您服务！";
        }
        
        welcomeTextView.setText(greeting);
    }

    private void setupVoiceInput() {
        voiceInputFab.setOnTouchListener((view, event) -> {
            switch (event.getAction()) {
                case MotionEvent.ACTION_DOWN:
                    startVoiceRecognition();
                    return true;
                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    stopVoiceRecognition();
                    return true;
            }
            return false;
        });
    }

    private void checkPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.RECORD_AUDIO},
                    PERMISSION_REQUEST_CODE);
        }
    }

    private void initializeSpeechRecognizer() {
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this);
        speechRecognizer.setRecognitionListener(new RecognitionListener() {
            @Override
            public void onReadyForSpeech(Bundle params) {
                // 准备开始说话
                displayArea.setText("请开始说话...");
            }

            @Override
            public void onBeginningOfSpeech() {
                // 开始说话
                displayArea.setText("正在聆听...");
            }

            @Override
            public void onRmsChanged(float rmsdB) {
                // 音量变化
            }

            @Override
            public void onBufferReceived(byte[] buffer) {
                // 接收到语音数据
            }

            @Override
            public void onEndOfSpeech() {
                // 说话结束
                displayArea.setText("正在处理...");
            }

            @Override
            public void onError(int error) {
                // 发生错误
                String message;
                switch (error) {
                    case SpeechRecognizer.ERROR_AUDIO:
                        message = "音频错误";
                        break;
                    case SpeechRecognizer.ERROR_CLIENT:
                        message = "客户端错误";
                        break;
                    case SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS:
                        message = "权限不足";
                        break;
                    case SpeechRecognizer.ERROR_NETWORK:
                        message = "网络错误";
                        break;
                    case SpeechRecognizer.ERROR_NETWORK_TIMEOUT:
                        message = "网络超时";
                        break;
                    case SpeechRecognizer.ERROR_NO_MATCH:
                        message = "未能匹配结果";
                        break;
                    case SpeechRecognizer.ERROR_RECOGNIZER_BUSY:
                        message = "识别器忙";
                        break;
                    case SpeechRecognizer.ERROR_SERVER:
                        message = "服务器错误";
                        break;
                    case SpeechRecognizer.ERROR_SPEECH_TIMEOUT:
                        message = "语音超时";
                        break;
                    default:
                        message = "未知错误";
                        break;
                }
                FeedbackUtils.showError(MainActivity.this, message);
                displayArea.setText("语音识别失败：" + message);
            }

            @Override
            public void onResults(Bundle results) {
                // 获取识别结果
                ArrayList<String> matches = results
                        .getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                if (matches != null && !matches.isEmpty()) {
                    String text = matches.get(0);
                    inputText.setText(text);
                    predictText(text);
                }
            }

            @Override
            public void onPartialResults(Bundle partialResults) {
                // 部分识别结果
                ArrayList<String> matches = partialResults
                        .getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                if (matches != null && !matches.isEmpty()) {
                    String text = matches.get(0);
                    inputText.setText(text);
                }
            }

            @Override
            public void onEvent(int eventType, Bundle params) {
                // 其他事件
            }
        });
    }

    private void startVoiceRecognition() {
        Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "zh-CN");
        speechRecognizer.startListening(intent);
        displayArea.setText("正在聆听...");
    }

    private void stopVoiceRecognition() {
        speechRecognizer.stopListening();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (speechRecognizer != null) {
            speechRecognizer.destroy();
        }
    }

    // 调用后端接口进行预测
    private void predictText(String userInput) {
        if (userInput.isEmpty()) {
            FeedbackUtils.showError(this, "请输入内容");
            return;
        }
        
        FeedbackUtils.showLoading(this);
        
        // 保存到搜索历史
        cacheManager.saveSearchHistory(userInput);
        
        OkHttpClient client = new OkHttpClient();
        MediaType mediaType = MediaType.parse("application/json");
        RequestBody body = RequestBody.create(mediaType, "{\"text\":\"" + userInput + "\"}");
        
        Request request = new Request.Builder()
                .url("http://your-backend-server.com/predict")
                .post(body)
                .build();
                
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                runOnUiThread(() -> {
                    FeedbackUtils.hideLoading();
                    FeedbackUtils.showSnackbar(
                        findViewById(android.R.id.content),
                        "网络连接失败",
                        "重试",
                        v -> predictText(userInput)
                    );
                });
            }
            
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                final String result = response.body().string();
                runOnUiThread(() -> {
                    FeedbackUtils.hideLoading();
                    displayArea.setText(result);
                    CustomAnimationUtils.fadeIn(displayArea);
                });
            }
        });
    }

    private void setupFunctionModules() {
        List<FunctionModule> modules = Arrays.asList(
            new FunctionModule(
                R.drawable.ic_express,
                "快递查询",
                "查询快递物流信息",
                getColor(R.color.module_express),
                ExpressQueryActivity.class
            ),
            new FunctionModule(
                R.drawable.ic_post_office,
                "网点查询",
                "查找附近邮政网点",
                getColor(R.color.module_post_office),
                PostOfficeActivity.class
            )
            // 添加更多功能模块...
        );

        functionModulesView.setLayoutManager(new GridLayoutManager(this, 2));
        functionModulesView.setAdapter(new FunctionModuleAdapter(modules));
    }

    private void setupQuickCommands() {
        // 从缓存获取快捷指令
        List<String> commands = cacheManager.getQuickCommands();
        
        for (String command : commands) {
            Chip chip = new Chip(this);
            chip.setText(command);
            chip.setCheckable(false);
            chip.setClickable(true);
            chip.setChipBackgroundColorResource(R.color.chip_background);
            chip.setOnClickListener(v -> {
                CustomAnimationUtils.pulseAnimation(v);
                handleQuickCommand(command);
            });
            quickCommandsGroup.addView(chip);
        }
    }

    private void handleQuickCommand(String command) {
        switch (command) {
            case "查快递":
                startActivity(new Intent(this, ExpressQueryActivity.class));
                break;
            case "找网点":
                startActivity(new Intent(this, PostOfficeActivity.class));
                break;
            // 处理其他快捷指令...
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.toolbar_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case android.R.id.home:
                // Handle navigation drawer
                return true;
            case R.id.action_notification:
                // Handle notification
                return true;
            case R.id.action_settings:
                // Handle settings
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }

    private boolean isAccessibilityServiceEnabled() {
        // 检查可访问性服务是否启用
        return false; // 实现具体检查逻辑
    }

    private void requestAccessibilityPermission() {
        // 请求启用可访问性服务
        Intent intent = new Intent(android.provider.Settings.ACTION_ACCESSIBILITY_SETTINGS);
        startActivity(intent);
    }
}