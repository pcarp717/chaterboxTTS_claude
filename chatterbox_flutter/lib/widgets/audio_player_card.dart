import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:math' as math;
import '../providers/app_providers.dart';

class AudioPlayerCard extends ConsumerStatefulWidget {
  const AudioPlayerCard({Key? key}) : super(key: key);

  @override
  ConsumerState<AudioPlayerCard> createState() => _AudioPlayerCardState();
}

class _AudioPlayerCardState extends ConsumerState<AudioPlayerCard>
    with TickerProviderStateMixin {
  late AnimationController _playButtonController;
  late AnimationController _waveAnimationController;
  late Animation<double> _playButtonAnimation;

  @override
  void initState() {
    super.initState();
    _playButtonController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    _waveAnimationController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    )..repeat();
    
    _playButtonAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _playButtonController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _playButtonController.dispose();
    _waveAnimationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final audioState = ref.watch(audioStateProvider);
    final playbackSpeed = ref.watch(playbackSpeedProvider);
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
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
                    Icons.music_note,
                    color: colorScheme.onPrimaryContainer,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'Audio Playback',
                  style: textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                if (audioState.isLoaded)
                  Chip(
                    label: Text(
                      '${audioState.duration?.toStringAsFixed(1)}s',
                      style: textTheme.bodySmall,
                    ),
                    backgroundColor: colorScheme.secondaryContainer,
                  ),
              ],
            ),
            
            const SizedBox(height: 20),
            
            if (!audioState.isLoaded) 
              _buildNoAudioState(context)
            else ...[
              // Waveform visualization
              _buildWaveform(context, audioState),
              
              const SizedBox(height: 20),
              
              // Progress bar
              _buildProgressBar(context, audioState),
              
              const SizedBox(height: 20),
              
              // Playback controls
              _buildPlaybackControls(context, audioState),
              
              const SizedBox(height: 20),
              
              // Speed control
              _buildSpeedControl(context, playbackSpeed),
              
              const SizedBox(height: 16),
              
              // Audio info
              _buildAudioInfo(context, audioState),
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildNoAudioState(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: colorScheme.surfaceVariant.withOpacity(0.3),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: colorScheme.outline.withOpacity(0.2),
          style: BorderStyle.solid,
        ),
      ),
      child: Column(
        children: [
          Icon(
            Icons.music_off,
            size: 48,
            color: colorScheme.onSurface.withOpacity(0.4),
          ),
          const SizedBox(height: 16),
          Text(
            'No audio loaded',
            style: textTheme.titleMedium?.copyWith(
              color: colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Generate speech to see playback controls',
            style: textTheme.bodyMedium?.copyWith(
              color: colorScheme.onSurface.withOpacity(0.4),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
  
  Widget _buildWaveform(BuildContext context, AudioState audioState) {
    final colorScheme = Theme.of(context).colorScheme;
    
    return Container(
      height: 80,
      decoration: BoxDecoration(
        color: colorScheme.primaryContainer.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: CustomPaint(
        painter: WaveformPainter(
          progress: audioState.progress,
          isPlaying: audioState.isPlaying,
          primaryColor: colorScheme.primary,
          backgroundColor: colorScheme.onSurface.withOpacity(0.1),
          animation: _waveAnimationController,
        ),
        size: const Size.fromHeight(80),
      ),
    );
  }
  
  Widget _buildProgressBar(BuildContext context, AudioState audioState) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    return Column(
      children: [
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            trackHeight: 6,
            thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 8),
            overlayShape: const RoundSliderOverlayShape(overlayRadius: 16),
          ),
          child: Slider(
            value: audioState.progress.clamp(0.0, 1.0),
            onChanged: (value) {
              ref.read(audioStateProvider.notifier).seekTo(value);
            },
            activeColor: colorScheme.primary,
            inactiveColor: colorScheme.surfaceVariant,
          ),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              _formatDuration(audioState.position ?? Duration.zero),
              style: textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
            Text(
              _formatDuration(audioState.duration ?? Duration.zero),
              style: textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
          ],
        ),
      ],
    );
  }
  
  Widget _buildPlaybackControls(BuildContext context, AudioState audioState) {
    final colorScheme = Theme.of(context).colorScheme;
    
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Previous/Restart button
        IconButton.filledTonal(
          onPressed: () => ref.read(audioServiceProvider).seekTo(Duration.zero),
          icon: const Icon(Icons.skip_previous),
          tooltip: 'Restart',
        ),
        
        const SizedBox(width: 16),
        
        // Main play/pause button
        GestureDetector(
          onTap: () {
            if (audioState.isPlaying) {
              ref.read(audioServiceProvider).pause();
              _playButtonController.reverse();
            } else {
              ref.read(audioServiceProvider).play();
              _playButtonController.forward();
            }
          },
          child: AnimatedBuilder(
            animation: _playButtonAnimation,
            builder: (context, child) {
              return Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: colorScheme.primary,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: colorScheme.primary.withOpacity(0.3),
                      blurRadius: 8,
                      spreadRadius: 0,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Icon(
                  audioState.isPlaying ? Icons.pause : Icons.play_arrow,
                  color: colorScheme.onPrimary,
                  size: 32,
                ),
              );
            },
          ),
        ),
        
        const SizedBox(width: 16),
        
        // Stop button
        IconButton.filledTonal(
          onPressed: () {
            ref.read(audioServiceProvider).stop();
            _playButtonController.reset();
          },
          icon: const Icon(Icons.stop),
          tooltip: 'Stop',
        ),
      ],
    );
  }
  
  Widget _buildSpeedControl(BuildContext context, double playbackSpeed) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    return Row(
      children: [
        Icon(
          Icons.speed,
          color: colorScheme.primary,
          size: 20,
        ),
        const SizedBox(width: 12),
        Text(
          'Playback Speed:',
          style: textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: SliderTheme(
            data: SliderTheme.of(context).copyWith(
              trackHeight: 4,
              thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
            ),
            child: Slider(
              value: playbackSpeed,
              min: 0.5,
              max: 2.0,
              divisions: 15,
              label: '${playbackSpeed.toStringAsFixed(1)}x',
              onChanged: (value) {
                ref.read(playbackSpeedProvider.notifier).state = value;
                ref.read(audioServiceProvider).setSpeed(value);
              },
            ),
          ),
        ),
        const SizedBox(width: 12),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            '${playbackSpeed.toStringAsFixed(1)}x',
            style: textTheme.labelMedium?.copyWith(
              color: colorScheme.onPrimaryContainer,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
  
  Widget _buildAudioInfo(BuildContext context, AudioState audioState) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colorScheme.surfaceVariant.withOpacity(0.5),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(
            Icons.info_outline,
            size: 16,
            color: colorScheme.onSurface.withOpacity(0.6),
          ),
          const SizedBox(width: 8),
          Text(
            'Sample Rate: ${audioState.sampleRate ?? 0} Hz | '
            'Format: WAV | '
            'Quality: High',
            style: textTheme.bodySmall?.copyWith(
              color: colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
        ],
      ),
    );
  }
  
  String _formatDuration(Duration duration) {
    final minutes = duration.inMinutes;
    final seconds = duration.inSeconds.remainder(60);
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }
}

class WaveformPainter extends CustomPainter {
  final double progress;
  final bool isPlaying;
  final Color primaryColor;
  final Color backgroundColor;
  final Animation<double> animation;
  
  WaveformPainter({
    required this.progress,
    required this.isPlaying,
    required this.primaryColor,
    required this.backgroundColor,
    required this.animation,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;
    
    final activePaint = Paint()
      ..color = primaryColor
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;
    
    final inactivePaint = Paint()
      ..color = backgroundColor
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;
    
    final barCount = (size.width / 4).floor();
    final barWidth = 2.0;
    final barSpacing = 2.0;
    final centerY = size.height / 2;
    
    for (int i = 0; i < barCount; i++) {
      final x = i * (barWidth + barSpacing);
      final normalizedPosition = i / barCount;
      
      // Generate pseudo-random wave heights
      final baseHeight = (math.sin(i * 0.5) * 0.5 + 0.5) * size.height * 0.6;
      final animationOffset = isPlaying 
        ? math.sin(animation.value * 2 * math.pi + i * 0.3) * 0.2 
        : 0;
      final height = (baseHeight + animationOffset * size.height * 0.2).abs();
      
      final paint = normalizedPosition <= progress ? activePaint : inactivePaint;
      
      canvas.drawLine(
        Offset(x, centerY - height / 2),
        Offset(x, centerY + height / 2),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}