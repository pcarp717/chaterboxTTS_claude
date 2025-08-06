import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/app_providers.dart';

class SystemMonitorCard extends ConsumerWidget {
  const SystemMonitorCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final systemStats = ref.watch(systemStatsProvider);
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.monitor_heart,
                    color: colorScheme.onPrimaryContainer,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'System Monitor',
                  style: textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            systemStats.when(
              data: (stats) => _buildSystemStats(context, stats),
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(),
                ),
              ),
              error: (error, stack) => _buildErrorState(context, error),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildSystemStats(BuildContext context, Map<String, dynamic> stats) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    return Column(
      children: [
        // Model status
        _buildStatusRow(
          context,
          'Model Status',
          stats['model_loaded'] ? 'Loaded' : 'Not Loaded',
          stats['model_loaded'] ? Colors.green : Colors.orange,
        ),
        
        const SizedBox(height: 12),
        
        // Device info
        _buildStatusRow(
          context,
          'Device',
          stats['device']?.toString().toUpperCase() ?? 'Unknown',
          colorScheme.primary,
        ),
        
        const SizedBox(height: 16),
        
        // Memory usage charts
        if (stats['ram_usage_percent'] != null)
          _buildMemoryChart(
            context,
            'RAM Usage',
            stats['ram_usage_percent'],
            colorScheme.secondary,
          ),
        
        if (stats['vram_usage_percent'] != null) ...[
          const SizedBox(height: 16),
          _buildMemoryChart(
            context,
            'VRAM Usage',
            stats['vram_usage_percent'],
            colorScheme.tertiary,
          ),
        ],
        
        const SizedBox(height: 16),
        
        // Additional stats
        if (stats['last_used'] != null)
          Text(
            'Last used: ${_getTimeAgo(stats['last_used'])}',
            style: textTheme.bodySmall?.copyWith(
              color: colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
      ],
    );
  }
  
  Widget _buildStatusRow(BuildContext context, String label, String value, Color color) {
    final textTheme = Theme.of(context).textTheme;
    
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: textTheme.bodyMedium,
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            value,
            style: textTheme.bodySmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
  
  Widget _buildMemoryChart(BuildContext context, String label, double percentage, Color color) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(
              '${percentage.toStringAsFixed(1)}%',
              style: textTheme.bodySmall?.copyWith(
                color: color,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          height: 8,
          decoration: BoxDecoration(
            color: colorScheme.surfaceVariant,
            borderRadius: BorderRadius.circular(4),
          ),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: (percentage / 100).clamp(0.0, 1.0),
            child: Container(
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ),
        ),
      ],
    );
  }
  
  Widget _buildErrorState(BuildContext context, Object error) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.errorContainer.withOpacity(0.3),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(
            Icons.error_outline,
            color: colorScheme.error,
            size: 32,
          ),
          const SizedBox(height: 8),
          Text(
            'Unable to load system stats',
            style: textTheme.bodyMedium?.copyWith(
              color: colorScheme.onErrorContainer,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Check if backend is running',
            style: textTheme.bodySmall?.copyWith(
              color: colorScheme.onErrorContainer.withOpacity(0.7),
            ),
          ),
        ],
      ),
    );
  }
  
  String _getTimeAgo(dynamic timestamp) {
    try {
      final lastUsed = DateTime.fromMillisecondsSinceEpoch(
        (timestamp * 1000).round(),
      );
      final now = DateTime.now();
      final difference = now.difference(lastUsed);
      
      if (difference.inMinutes < 1) {
        return 'Just now';
      } else if (difference.inHours < 1) {
        return '${difference.inMinutes}m ago';
      } else if (difference.inDays < 1) {
        return '${difference.inHours}h ago';
      } else {
        return '${difference.inDays}d ago';
      }
    } catch (e) {
      return 'Unknown';
    }
  }
}