class WatchContext(private val service: AutomationService) {
    private val watchers = mutableListOf<AutomationWatcher>()
    
    fun when(condition: String): WatchBuilder {
        return WatchBuilder(this, condition)
    }

    fun waitStable(timeout: Long = 10000) {
        // 等待界面稳定,参考uiautomator2实现
    }
    
    fun close() {
        watchers.clear()
    }
} 