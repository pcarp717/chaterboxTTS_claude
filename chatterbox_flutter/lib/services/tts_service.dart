import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import '../providers/app_providers.dart';

class TTSService {
  final Ref ref;
  static const String _baseUrl = 'http://localhost:8000'; // Python backend
  
  TTSService(this.ref);
  
  Future<void> generateSpeech({
    required String text,
    required String voiceProfile,
    double? exaggeration,
    double? cfgWeight,
  }) async {
    if (text.trim().isEmpty) {
      throw Exception('Text cannot be empty');
    }
    
    if (text.length > 10000) {
      throw Exception('Text exceeds 10,000 character limit');
    }
    
    try {
      // Update generation state
      ref.read(isGeneratingProvider.notifier).state = true;
      ref.read(generationProgressProvider.notifier).state = 0.0;
      ref.read(generationStatusProvider.notifier).state = 'Starting generation...';
      
      final requestBody = {
        'text': text,
        'voice_profile': voiceProfile,
        'exaggeration': exaggeration ?? ref.read(exaggerationProvider),
        'cfg_weight': cfgWeight ?? ref.read(cfgWeightProvider),
      };
      
      // Update progress
      ref.read(generationProgressProvider.notifier).state = 0.2;
      ref.read(generationStatusProvider.notifier).state = 'Processing text...';
      
      final response = await http.post(
        Uri.parse('$_baseUrl/generate'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(requestBody),
      );
      
      ref.read(generationProgressProvider.notifier).state = 0.6;
      ref.read(generationStatusProvider.notifier).state = 'Generating audio...';
      
      if (response.statusCode == 200) {
        final responseData = json.decode(response.body);
        
        ref.read(generationProgressProvider.notifier).state = 0.9;
        ref.read(generationStatusProvider.notifier).state = 'Loading audio...';
        
        // Load audio into player
        final audioPath = responseData['audio_path'] as String;
        final duration = Duration(
          milliseconds: (responseData['duration'] * 1000).round(),
        );
        final sampleRate = responseData['sample_rate'] as int;
        
        // Update audio state
        ref.read(audioStateProvider.notifier).loadAudio(
          duration: duration,
          sampleRate: sampleRate,
          filePath: audioPath,
        );
        
        // Auto-play the audio
        await ref.read(audioServiceProvider).loadFile(audioPath);
        await ref.read(audioServiceProvider).play();
        
        final generationTime = responseData['generation_time'] as double;
        final speedRatio = duration.inMilliseconds / 1000 / generationTime;
        
        ref.read(generationStatusProvider.notifier).state = 
          'Generated ${duration.inSeconds.toStringAsFixed(1)}s audio in '
          '${generationTime.toStringAsFixed(1)}s (${speedRatio.toStringAsFixed(1)}x real-time)';
        
        ref.read(generationProgressProvider.notifier).state = 1.0;
        
      } else {
        throw Exception('Server error: ${response.statusCode}');
      }
      
    } catch (e) {
      ref.read(generationStatusProvider.notifier).state = 'Error: $e';
      throw e;
    } finally {
      ref.read(isGeneratingProvider.notifier).state = false;
    }
  }
  
  Future<bool> isServerRunning() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));
      
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
  
  Future<void> startPythonBackend() async {
    try {
      // Start the Python backend process
      final process = await Process.start(
        'python',
        ['python_backend/main.py'],
        workingDirectory: Directory.current.path,
      );
      
      // Wait for server to start
      await Future.delayed(const Duration(seconds: 3));
      
      // Check if server is running
      if (!await isServerRunning()) {
        throw Exception('Failed to start Python backend');
      }
      
    } catch (e) {
      throw Exception('Could not start TTS backend: $e');
    }
  }
  
  Future<Map<String, dynamic>> getSystemStats() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/system/stats'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get system stats');
      }
    } catch (e) {
      // Return mock data if backend is not available
      return {
        'model_loaded': false,
        'device': 'Unknown',
        'ram_usage_percent': 0.0,
        'vram_used': 0.0,
        'vram_total': 0.0,
        'vram_usage_percent': 0.0,
        'last_used': null,
      };
    }
  }
}