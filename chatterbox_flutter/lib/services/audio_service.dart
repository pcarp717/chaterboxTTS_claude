import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:audioplayers/audioplayers.dart';
import 'dart:async';
import '../providers/app_providers.dart';

class AudioService {
  final Ref ref;
  late AudioPlayer _audioPlayer;
  StreamSubscription<Duration>? _positionSubscription;
  StreamSubscription<Duration>? _durationSubscription;
  StreamSubscription<PlayerState>? _stateSubscription;
  
  AudioService(this.ref) {
    _audioPlayer = AudioPlayer();
    _setupSubscriptions();
  }
  
  void _setupSubscriptions() {
    // Position updates
    _positionSubscription = _audioPlayer.onPositionChanged.listen((position) {
      final state = ref.read(audioStateProvider);
      if (state.duration != null && state.duration!.inMilliseconds > 0) {
        final progress = position.inMilliseconds / state.duration!.inMilliseconds;
        ref.read(audioStateProvider.notifier).updatePlaybackState(
          position: position,
          progress: progress.clamp(0.0, 1.0),
        );
      }
    });
    
    // Duration updates
    _durationSubscription = _audioPlayer.onDurationChanged.listen((duration) {
      ref.read(audioStateProvider.notifier).loadAudio(
        duration: duration,
        sampleRate: ref.read(audioStateProvider).sampleRate ?? 48000,
      );
    });
    
    // State changes
    _stateSubscription = _audioPlayer.onPlayerStateChanged.listen((state) {
      final isPlaying = state == PlayerState.playing;
      final isPaused = state == PlayerState.paused;
      
      ref.read(audioStateProvider.notifier).updatePlaybackState(
        isPlaying: isPlaying,
      );
    });
  }
  
  Future<void> loadFile(String filePath) async {
    try {
      await _audioPlayer.setSource(DeviceFileSource(filePath));
    } catch (e) {
      throw Exception('Failed to load audio file: $e');
    }
  }
  
  Future<void> loadUrl(String url) async {
    try {
      await _audioPlayer.setSource(UrlSource(url));
    } catch (e) {
      throw Exception('Failed to load audio from URL: $e');
    }
  }
  
  Future<void> play() async {
    try {
      await _audioPlayer.resume();
    } catch (e) {
      throw Exception('Failed to play audio: $e');
    }
  }
  
  Future<void> pause() async {
    try {
      await _audioPlayer.pause();
    } catch (e) {
      throw Exception('Failed to pause audio: $e');
    }
  }
  
  Future<void> stop() async {
    try {
      await _audioPlayer.stop();
      ref.read(audioStateProvider.notifier).updatePlaybackState(
        position: Duration.zero,
        progress: 0.0,
      );
    } catch (e) {
      throw Exception('Failed to stop audio: $e');
    }
  }
  
  Future<void> seekTo(Duration position) async {
    try {
      await _audioPlayer.seek(position);
    } catch (e) {
      throw Exception('Failed to seek audio: $e');
    }
  }
  
  Future<void> setSpeed(double speed) async {
    try {
      await _audioPlayer.setPlaybackRate(speed);
    } catch (e) {
      throw Exception('Failed to set playback speed: $e');
    }
  }
  
  Future<void> setVolume(double volume) async {
    try {
      await _audioPlayer.setVolume(volume.clamp(0.0, 1.0));
    } catch (e) {
      throw Exception('Failed to set volume: $e');
    }
  }
  
  Duration? get currentPosition => _audioPlayer.getDuration() as Duration?;
  Duration? get totalDuration => _audioPlayer.getDuration() as Duration?;
  
  bool get isPlaying => _audioPlayer.state == PlayerState.playing;
  bool get isPaused => _audioPlayer.state == PlayerState.paused;
  bool get isStopped => _audioPlayer.state == PlayerState.stopped;
  
  void dispose() {
    _positionSubscription?.cancel();
    _durationSubscription?.cancel();
    _stateSubscription?.cancel();
    _audioPlayer.dispose();
  }
}