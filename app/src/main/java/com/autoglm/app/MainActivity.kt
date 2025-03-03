class MainActivity : AppCompatActivity() {
    private lateinit var automationService: AutomationService
    private lateinit var llmService: LLMService
    private lateinit var webSocketService: WebSocketService
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // 初始化服务
        automationService = AutomationService(this)
        llmService = LLMService()
        webSocketService = WebSocketService()
        
        // 请求必要权限
        requestPermissions()
        
        // 设置UI监听器
        setupListeners()
    }
    
    private fun requestPermissions() {
        // 请求必要权限：无障碍服务、存储、麦克风等
    }
    
    private fun setupListeners() {
        // 设置语音输入按钮
        findViewById<Button>(R.id.btnVoiceInput).setOnClickListener {
            startVoiceInput()
        }
        
        // 设置文本输入按钮
        findViewById<Button>(R.id.btnTextInput).setOnClickListener {
            showTextInputDialog()
        }
    }
} 