import re
from datetime import datetime
from collections import defaultdict

class LogAnalyzer:
    def __init__(self, log_file):
        self.log_file = log_file
        
    def analyze_errors(self, start_time=None, end_time=None):
        """分析错误日志"""
        error_stats = defaultdict(int)
        error_details = []
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if 'ERROR' not in line:
                    continue
                    
                timestamp = self._extract_timestamp(line)
                if not self._is_in_timerange(timestamp, start_time, end_time):
                    continue
                    
                error_type = self._extract_error_type(line)
                error_stats[error_type] += 1
                error_details.append(line.strip())
                
        return {
            'stats': dict(error_stats),
            'details': error_details
        }
        
    def analyze_task_performance(self, task_id):
        """分析特定任务的执行性能"""
        task_logs = []
        execution_time = 0
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if f'[Task:{task_id}]' in line:
                    task_logs.append(line.strip())
                    
        # 分析任务执行时间和性能
        return {
            'execution_time': execution_time,
            'logs': task_logs
        }
        
    @staticmethod
    def _extract_timestamp(log_line):
        match = re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', log_line)
        if match:
            return datetime.strptime(match.group(), '%Y-%m-%d %H:%M:%S')
        return None
        
    @staticmethod
    def _extract_error_type(log_line):
        match = re.search(r'\[(\w+Error)\]', log_line)
        return match.group(1) if match else 'UnknownError'
        
    @staticmethod
    def _is_in_timerange(timestamp, start_time, end_time):
        if not timestamp:
            return False
        if start_time and timestamp < start_time:
            return False
        if end_time and timestamp > end_time:
            return False
        return True 