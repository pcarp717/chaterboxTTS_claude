import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class SimpleHomeScreen extends ConsumerStatefulWidget {
  const SimpleHomeScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<SimpleHomeScreen> createState() => _SimpleHomeScreenState();
}

class _SimpleHomeScreenState extends ConsumerState<SimpleHomeScreen> {
  final TextEditingController _textController = TextEditingController();
  bool _isGenerating = false;
  String _status = 'Checking backend...';

  @override
  void initState() {
    super.initState();
    _checkBackendHealth();
  }

  Future<void> _checkBackendHealth() async {
    try {
      final response = await http.get(Uri.parse('http://localhost:8000/health'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final ttsAvailable = data['tts_available'] ?? false;
        final message = data['message'] ?? 'Backend connected';
        
        setState(() => _status = ttsAvailable 
          ? '✅ Ready - Real TTS available' 
          : '⚠️ Ready - Demo mode (TTS not available)');
      } else {
        setState(() => _status = '❌ Backend error: ${response.statusCode}');
      }
    } catch (e) {
      setState(() => _status = '❌ Backend not running - Start Python backend first');
    }
  }

  Future<void> _generateSpeech() async {
    if (_textController.text.trim().isEmpty) return;

    setState(() {
      _isGenerating = true;
      _status = 'Generating speech...';
    });

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/generate'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'text': _textController.text.trim(),
          'voice': 'default'
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final status = data['status'];
        final message = data['message'];
        
        if (status == 'success') {
          final duration = data['duration'];
          final genTime = data['generation_time'];
          final audioPath = data['audio_path'];
          setState(() => _status = '✅ $message\n📁 Saved: $audioPath');
        } else if (status == 'demo') {
          setState(() => _status = '⚠️ $message\n💡 ${data['note']}');
        } else if (status == 'error') {
          setState(() => _status = '❌ $message');
        } else {
          setState(() => _status = '✅ $message');
        }
      } else {
        setState(() => _status = '❌ HTTP Error: ${response.statusCode}');
      }
    } catch (e) {
      setState(() => _status = '❌ Error: Backend not running\nMake sure Python backend is started');
    }

    setState(() => _isGenerating = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ChatterboxTTS Desktop'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Text to Speech',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _textController,
                      maxLines: 5,
                      decoration: const InputDecoration(
                        hintText: 'Enter text to convert to speech...',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton(
                            onPressed: _isGenerating ? null : _generateSpeech,
                            child: _isGenerating
                                ? const CircularProgressIndicator()
                                : const Text('Generate Speech'),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Backend Status',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        IconButton(
                          icon: const Icon(Icons.refresh),
                          onPressed: _checkBackendHealth,
                          tooltip: 'Check backend status',
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _status,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}