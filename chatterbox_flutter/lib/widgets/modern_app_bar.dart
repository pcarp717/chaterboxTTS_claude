import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_providers.dart';

class ModernAppBar extends ConsumerWidget implements PreferredSizeWidget {
  const ModernAppBar({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final themeMode = ref.watch(themeModeProvider);
    
    return AppBar(
      elevation: 0,
      backgroundColor: colorScheme.surface,
      surfaceTintColor: colorScheme.surfaceTint,
      centerTitle: false,
      title: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: colorScheme.primaryContainer,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              Icons.record_voice_over,
              color: colorScheme.onPrimaryContainer,
              size: 24,
            ),
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'ChatterboxTTS',
                style: textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                'Modern Desktop',
                style: textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurface.withOpacity(0.6),
                ),
              ),
            ],
          ),
        ],
      ),
      actions: [
        // Theme toggle
        IconButton.filledTonal(
          onPressed: () {
            final newMode = themeMode == ThemeMode.light 
              ? ThemeMode.dark 
              : ThemeMode.light;
            ref.read(themeModeProvider.notifier).state = newMode;
          },
          icon: Icon(
            themeMode == ThemeMode.light 
              ? Icons.dark_mode 
              : Icons.light_mode,
          ),
          tooltip: 'Toggle theme',
        ),
        
        const SizedBox(width: 8),
        
        // System status indicator
        Consumer(
          builder: (context, ref, child) {
            final systemStats = ref.watch(systemStatsProvider);
            
            return systemStats.when(
              data: (stats) => _buildSystemStatusChip(context, stats),
              loading: () => const Padding(
                padding: EdgeInsets.all(16),
                child: SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
              error: (error, stack) => IconButton(
                onPressed: () => _showSystemError(context, error),
                icon: Icon(
                  Icons.error,
                  color: colorScheme.error,
                ),
              ),
            );
          },
        ),
        
        const SizedBox(width: 8),
        
        // Window controls (minimize, maximize, close)
        _buildWindowControls(context),
        
        const SizedBox(width: 16),
      ],
    );
  }
  
  Widget _buildSystemStatusChip(BuildContext context, Map<String, dynamic> stats) {
    final colorScheme = Theme.of(context).colorScheme;
    final isModelLoaded = stats['model_loaded'] ?? false;
    
    return Chip(
      avatar: Icon(
        isModelLoaded ? Icons.check_circle : Icons.circle_outlined,
        size: 16,
        color: isModelLoaded 
          ? colorScheme.primary 
          : colorScheme.onSurface.withOpacity(0.6),
      ),
      label: Text(
        isModelLoaded ? 'Ready' : 'Idle',
        style: Theme.of(context).textTheme.bodySmall,
      ),
      backgroundColor: isModelLoaded 
        ? colorScheme.primaryContainer 
        : colorScheme.surfaceVariant,
      padding: const EdgeInsets.symmetric(horizontal: 8),
    );
  }
  
  Widget _buildWindowControls(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    
    return Row(
      children: [
        // Minimize
        InkWell(
          onTap: () {
            // TODO: Implement minimize
          },
          borderRadius: BorderRadius.circular(6),
          child: Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(
              Icons.remove,
              size: 16,
              color: colorScheme.onSurface.withOpacity(0.7),
            ),
          ),
        ),
        
        // Maximize/Restore
        InkWell(
          onTap: () {
            // TODO: Implement maximize/restore
          },
          borderRadius: BorderRadius.circular(6),
          child: Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(
              Icons.crop_square,
              size: 16,
              color: colorScheme.onSurface.withOpacity(0.7),
            ),
          ),
        ),
        
        // Close
        InkWell(
          onTap: () {
            // TODO: Implement close with confirmation
          },
          borderRadius: BorderRadius.circular(6),
          child: Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(
              Icons.close,
              size: 16,
              color: colorScheme.error,
            ),
          ),
        ),
      ],
    );
  }
  
  void _showSystemError(BuildContext context, Object error) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('System Error'),
        content: Text(error.toString()),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}