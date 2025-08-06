import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/tts_service.dart';
import '../services/audio_service.dart';
import '../services/theme_service.dart';
import '../models/audio_state.dart';
import '../models/voice_profile.dart';

// Theme Management
final themeModeProvider = StateProvider<ThemeMode>((ref) => ThemeMode.system);

// Text Input Management
final textControllerProvider = Provider<TextEditingController>((ref) {
  final controller = TextEditingController();
  ref.onDispose(() => controller.dispose());
  return controller;
});

final characterCountProvider = StateProvider<int>((ref) => 0);

// Voice Settings
final exaggerationProvider = StateProvider<double>((ref) => 0.5);
final cfgWeightProvider = StateProvider<double>((ref) => 0.5);
final playbackSpeedProvider = StateProvider<double>((ref) => 1.0);

// Voice Selection
final selectedVoiceProvider = StateProvider<String>((ref) => 'Default');
final availableVoicesProvider = StateProvider<List<VoiceProfile>>((ref) => [
  VoiceProfile(
    id: 'default',
    name: 'Default',
    description: 'High-quality default voice',
    isCustom: false,
  ),
]);

// Generation State
final isGeneratingProvider = StateProvider<bool>((ref) => false);
final generationProgressProvider = StateProvider<double>((ref) => 0.0);
final generationStatusProvider = StateProvider<String>((ref) => 'Ready to generate speech');

// Audio Management
final audioStateProvider = StateNotifierProvider<AudioStateNotifier, AudioState>((ref) {
  return AudioStateNotifier();
});

final playbackSpeedNotifierProvider = StateNotifierProvider<PlaybackSpeedNotifier, double>((ref) {
  return PlaybackSpeedNotifier();
});

// Services
final ttsServiceProvider = Provider<TTSService>((ref) {
  return TTSService(ref);
});

final audioServiceProvider = Provider<AudioService>((ref) {
  return AudioService(ref);
});

// System Monitoring
final systemStatsProvider = StreamProvider<Map<String, dynamic>>((ref) {
  return Stream.periodic(
    const Duration(seconds: 5),
    (_) => _getSystemStats(),
  );
});

// Audio State Notifier
class AudioStateNotifier extends StateNotifier<AudioState> {
  AudioStateNotifier() : super(AudioState.initial());
  
  void loadAudio({
    required Duration duration,
    required int sampleRate,
    String? filePath,
  }) {
    state = state.copyWith(
      isLoaded: true,
      duration: duration,
      sampleRate: sampleRate,
      filePath: filePath,
    );
  }
  
  void updatePlaybackState({
    bool? isPlaying,
    Duration? position,
    double? progress,
  }) {
    state = state.copyWith(
      isPlaying: isPlaying ?? state.isPlaying,
      position: position ?? state.position,
      progress: progress ?? state.progress,
    );
  }
  
  void seekTo(double progress) {
    if (state.duration != null) {
      final newPosition = Duration(
        milliseconds: (state.duration!.inMilliseconds * progress).round(),
      );
      state = state.copyWith(
        position: newPosition,
        progress: progress,
      );
    }
  }
  
  void reset() {
    state = AudioState.initial();
  }
}

// Playback Speed Notifier
class PlaybackSpeedNotifier extends StateNotifier<double> {
  PlaybackSpeedNotifier() : super(1.0);
  
  void setSpeed(double speed) {
    state = speed.clamp(0.5, 2.0);
  }
  
  void increment() {
    setSpeed(state + 0.1);
  }
  
  void decrement() {
    setSpeed(state - 0.1);
  }
  
  void reset() {
    state = 1.0;
  }
}

// System Stats Mock Function (replace with actual system monitoring)
Map<String, dynamic> _getSystemStats() {
  return {
    'model_loaded': false, // Will be updated by actual TTS service
    'device': 'CUDA',
    'ram_usage_percent': 45.2,
    'vram_used': 2.1,
    'vram_total': 8.0,
    'vram_usage_percent': 26.25,
    'last_used': DateTime.now().millisecondsSinceEpoch / 1000,
    'temperature': 65,
    'power_usage': 85,
  };
}

// Voice Management Providers
final voiceManagementProvider = StateNotifierProvider<VoiceManagementNotifier, VoiceManagementState>((ref) {
  return VoiceManagementNotifier();
});

class VoiceManagementNotifier extends StateNotifier<VoiceManagementState> {
  VoiceManagementNotifier() : super(VoiceManagementState.initial());
  
  Future<void> addVoice({
    required String name,
    required String filePath,
  }) async {
    state = state.copyWith(isLoading: true);
    
    try {
      // TODO: Implement actual voice addition logic
      await Future.delayed(const Duration(seconds: 2)); // Simulate processing
      
      final newVoice = VoiceProfile(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        name: name,
        description: 'Custom voice clone',
        isCustom: true,
        filePath: filePath,
        createdAt: DateTime.now(),
      );
      
      state = state.copyWith(
        voices: [...state.voices, newVoice],
        isLoading: false,
        message: 'Voice "$name" added successfully!',
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to add voice: $e',
      );
    }
  }
  
  void removeVoice(String voiceId) {
    state = state.copyWith(
      voices: state.voices.where((v) => v.id != voiceId).toList(),
      message: 'Voice removed successfully',
    );
  }
  
  void clearMessage() {
    state = state.copyWith(message: null, error: null);
  }
}

class VoiceManagementState {
  final List<VoiceProfile> voices;
  final bool isLoading;
  final String? message;
  final String? error;
  
  const VoiceManagementState({
    required this.voices,
    required this.isLoading,
    this.message,
    this.error,
  });
  
  static VoiceManagementState initial() {
    return VoiceManagementState(
      voices: [
        VoiceProfile(
          id: 'default',
          name: 'Default',
          description: 'High-quality default voice',
          isCustom: false,
        ),
      ],
      isLoading: false,
    );
  }
  
  VoiceManagementState copyWith({
    List<VoiceProfile>? voices,
    bool? isLoading,
    String? message,
    String? error,
  }) {
    return VoiceManagementState(
      voices: voices ?? this.voices,
      isLoading: isLoading ?? this.isLoading,
      message: message ?? this.message,
      error: error ?? this.error,
    );
  }
}