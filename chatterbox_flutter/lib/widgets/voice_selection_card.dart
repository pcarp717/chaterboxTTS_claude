import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_providers.dart';
import '../models/voice_profile.dart';

class VoiceSelectionCard extends ConsumerWidget {
  const VoiceSelectionCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final selectedVoice = ref.watch(selectedVoiceProvider);
    final voiceManagement = ref.watch(voiceManagementProvider);
    
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
                    Icons.person,
                    color: colorScheme.onPrimaryContainer,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'Voice Selection',
                  style: textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                Chip(
                  label: Text('${voiceManagement.voices.length} voices'),
                  backgroundColor: colorScheme.secondaryContainer,
                ),
              ],
            ),
            
            const SizedBox(height: 20),
            
            // Voice dropdown
            DropdownButtonFormField<String>(
              value: selectedVoice,
              decoration: InputDecoration(
                labelText: 'Select Voice',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                filled: true,
                fillColor: colorScheme.surface,
              ),
              items: voiceManagement.voices.map((voice) {
                return DropdownMenuItem<String>(
                  value: voice.name,
                  child: Row(
                    children: [
                      Icon(
                        voice.isCustom ? Icons.person : Icons.record_voice_over,
                        size: 20,
                        color: voice.isCustom 
                          ? colorScheme.secondary 
                          : colorScheme.primary,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              voice.name,
                              style: textTheme.bodyMedium?.copyWith(
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            if (voice.isCustom)
                              Text(
                                'Custom Voice',
                                style: textTheme.bodySmall?.copyWith(
                                  color: colorScheme.secondary,
                                ),
                              ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null) {
                  ref.read(selectedVoiceProvider.notifier).state = value;
                }
              },
            ),
            
            const SizedBox(height: 16),
            
            // Voice info display
            _buildVoiceInfo(context, ref, selectedVoice, voiceManagement.voices),
            
            const SizedBox(height: 16),
            
            // Quick voice test button
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _testVoice(context, ref, selectedVoice),
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('Test Voice'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _showVoiceDetails(context, selectedVoice, voiceManagement.voices),
                    icon: const Icon(Icons.info_outline),
                    label: const Text('Details'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildVoiceInfo(
    BuildContext context, 
    WidgetRef ref, 
    String selectedVoice, 
    List<VoiceProfile> voices
  ) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    final voice = voices.firstWhere(
      (v) => v.name == selectedVoice,
      orElse: () => voices.first,
    );
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surfaceVariant.withOpacity(0.3),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: colorScheme.outline.withOpacity(0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                voice.isCustom ? Icons.person : Icons.record_voice_over,
                color: voice.isCustom 
                  ? colorScheme.secondary 
                  : colorScheme.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                voice.name,
                style: textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              if (voice.isCustom) ...[
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: colorScheme.secondaryContainer,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    'CUSTOM',
                    style: textTheme.labelSmall?.copyWith(
                      color: colorScheme.onSecondaryContainer,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ],
          ),
          
          const SizedBox(height: 8),
          
          Text(
            voice.description,
            style: textTheme.bodyMedium?.copyWith(
              color: colorScheme.onSurface.withOpacity(0.8),
            ),
          ),
          
          if (voice.isCustom && voice.createdAt != null) ...[
            const SizedBox(height: 8),
            Text(
              'Created: ${_formatDate(voice.createdAt!)}',
              style: textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
          ],
          
          if (voice.duration != null) ...[
            const SizedBox(height: 4),
            Text(
              'Sample Duration: ${voice.duration!.toStringAsFixed(1)}s',
              style: textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
          ],
        ],
      ),
    );
  }
  
  void _testVoice(BuildContext context, WidgetRef ref, String voiceName) {
    final testText = "Hello, this is a test of the $voiceName voice.";
    
    // Set test text
    final textController = ref.read(textControllerProvider);
    textController.text = testText;
    ref.read(characterCountProvider.notifier).state = testText.length;
    
    // Trigger generation
    ref.read(ttsServiceProvider).generateSpeech(
      text: testText,
      voiceProfile: voiceName,
    );
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Testing $voiceName voice...'),
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 2),
      ),
    );
  }
  
  void _showVoiceDetails(BuildContext context, String voiceName, List<VoiceProfile> voices) {
    final voice = voices.firstWhere((v) => v.name == voiceName);
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              voice.isCustom ? Icons.person : Icons.record_voice_over,
              color: voice.isCustom 
                ? Theme.of(context).colorScheme.secondary 
                : Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(width: 8),
            Text(voice.name),
          ],
        ),
        content: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildDetailRow('Type', voice.isCustom ? 'Custom Voice Clone' : 'Built-in Voice'),
            _buildDetailRow('Description', voice.description),
            if (voice.createdAt != null)
              _buildDetailRow('Created', _formatDate(voice.createdAt!)),
            if (voice.duration != null)
              _buildDetailRow('Duration', '${voice.duration!.toStringAsFixed(1)}s'),
            if (voice.sampleRate != null)
              _buildDetailRow('Sample Rate', '${voice.sampleRate} Hz'),
            if (voice.filePath != null)
              _buildDetailRow('Source File', voice.filePath!.split('/').last),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
  
  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }
  
  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}