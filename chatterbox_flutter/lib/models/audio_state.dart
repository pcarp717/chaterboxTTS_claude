class AudioState {
  final bool isLoaded;
  final bool isPlaying;
  final bool isPaused;
  final Duration? duration;
  final Duration? position;
  final double progress;
  final int? sampleRate;
  final String? filePath;
  
  const AudioState({
    required this.isLoaded,
    required this.isPlaying,
    required this.isPaused,
    this.duration,
    this.position,
    required this.progress,
    this.sampleRate,
    this.filePath,
  });
  
  factory AudioState.initial() {
    return const AudioState(
      isLoaded: false,
      isPlaying: false,
      isPaused: false,
      progress: 0.0,
    );
  }
  
  AudioState copyWith({
    bool? isLoaded,
    bool? isPlaying,
    bool? isPaused,
    Duration? duration,
    Duration? position,
    double? progress,
    int? sampleRate,
    String? filePath,
  }) {
    return AudioState(
      isLoaded: isLoaded ?? this.isLoaded,
      isPlaying: isPlaying ?? this.isPlaying,
      isPaused: isPaused ?? this.isPaused,
      duration: duration ?? this.duration,
      position: position ?? this.position,
      progress: progress ?? this.progress,
      sampleRate: sampleRate ?? this.sampleRate,
      filePath: filePath ?? this.filePath,
    );
  }
  
  @override
  String toString() {
    return 'AudioState(isLoaded: $isLoaded, isPlaying: $isPlaying, '
           'duration: $duration, position: $position, progress: $progress)';
  }
}