@Entity(tableName = "tasks")
data class Task(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val deviceId: String,
    val userInput: String,
    var status: String = "pending",
    val createdAt: Long = System.currentTimeMillis(),
    var updatedAt: Long = System.currentTimeMillis(),
    var executionSteps: List<AutomationAction>,
    var result: Map<String, Any>? = null
) 