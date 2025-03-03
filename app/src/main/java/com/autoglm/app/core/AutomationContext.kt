class AutomationContext(
    private val service: AutomationService,
    private val device: Device
) {
    // 基于uiautomator2的watch_context机制
    fun withWatchContext(block: WatchContext.() -> Unit) {
        val context = WatchContext(service)
        try {
            context.block()
            context.waitStable() 
        } finally {
            context.close()
        }
    }
    
    // 基于Airtest的断言机制
    fun assertExists(target: AutomationTarget) {
        when(target) {
            is ImageTarget -> assertImageExists(target.template)
            is ElementTarget -> assertElementExists(target.selector)
        }
    }
} 