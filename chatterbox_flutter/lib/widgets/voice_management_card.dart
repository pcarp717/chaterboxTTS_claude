import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../providers/app_providers.dart';

class VoiceManagementCard extends ConsumerStatefulWidget {
  const VoiceManagementCard({Key? key}) : super(key: key);

  @override
  ConsumerState<VoiceManagementCard> createState() => _VoiceManagementCardState();
}

class _VoiceManagementCardState extends ConsumerState<VoiceManagementCard> {
  final _nameController = TextEditingController();
  String? _selectedFilePath;
  
  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final voiceManagement = ref.watch(voiceManagementProvider);
    
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
                    Icons.manage_accounts,
                    color: colorScheme.onPrimaryContainer,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'Voice Management',
                  style: textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Add new voice section
            _buildAddVoiceSection(context, voiceManagement),
            
            const SizedBox(height: 16),
            
            // Existing voices list
            _buildVoicesList(context, voiceManagement),
            
            // Status messages
            if (voiceManagement.message != null || voiceManagement.error != null)
              _buildStatusMessage(context, voiceManagement),
          ],
        ),
      ),
    );
  }
  
  Widget _buildAddVoiceSection(BuildContext context, VoiceManagementState state) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
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
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Add New Voice',
            style: textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          
          // Voice name input
          TextField(
            controller: _nameController,
            decoration: const InputDecoration(
              labelText: 'Voice Name',
              hintText: 'e.g., My Voice, John\'s Voice',
              isDense: true,
            ),
            enabled: !state.isLoading,
          ),
          
          const SizedBox(height: 12),
          
          // File picker button
          OutlinedButton.icon(
            onPressed: state.isLoading ? null : _pickAudioFile,
            icon: const Icon(Icons.upload_file),
            label: Text(_selectedFilePath != null 
              ? 'Audio: ${_selectedFilePath!.split('/').last}'
              : 'Select Audio File'),
          ),
          
          if (_selectedFilePath != null) ...[
            const SizedBox(height: 8),
            Text(
              'Selected: ${_selectedFilePath!.split('/').last}',
              style: textTheme.bodySmall?.copyWith(
                color: colorScheme.primary,
              ),
            ),
          ],
          
          const SizedBox(height: 12),
          
          // Add button
          ElevatedButton.icon(
            onPressed: state.isLoading || 
                      _nameController.text.trim().isEmpty || 
                      _selectedFilePath == null
              ? null
              : _addVoice,
            icon: state.isLoading 
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.add),
            label: Text(state.isLoading ? 'Adding...' : 'Add Voice'),
          ),
          
          const SizedBox(height: 8),
          
          Text(
            'Upload a 7-20 second clear audio sample (WAV or MP3)',
            style: textTheme.bodySmall?.copyWith(
              color: colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildVoicesList(BuildContext context, VoiceManagementState state) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    final customVoices = state.voices.where((v) => v.isCustom).toList();
    
    if (customVoices.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: colorScheme.surfaceVariant.withOpacity(0.3),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Icon(
              Icons.voice_over_off,
              size: 32,
              color: colorScheme.onSurface.withOpacity(0.4),
            ),
            const SizedBox(height: 8),
            Text(
              'No custom voices',
              style: textTheme.bodyMedium?.copyWith(
                color: colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
            Text(
              'Add your first custom voice above',
              style: textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurface.withOpacity(0.4),
              ),
            ),
          ],
        ),
      );
    }
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Custom Voices (${customVoices.length})',
          style: textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        ...customVoices.map((voice) => _buildVoiceItem(context, voice)),
      ],
    );
  }
  
  Widget _buildVoiceItem(BuildContext context, voice) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colorScheme.surfaceVariant.withOpacity(0.5),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(
            Icons.person,
            color: colorScheme.secondary,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  voice.name,
                  style: textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                ),
                if (voice.createdAt != null)
                  Text(
                    'Created ${_formatDate(voice.createdAt!)}',
                    style: textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurface.withOpacity(0.6),
                    ),
                  ),
              ],
            ),
          ),
          IconButton(
            onPressed: () => _confirmDeleteVoice(context, voice),
            icon: const Icon(Icons.delete_outline),
            color: colorScheme.error,
            tooltip: 'Delete voice',
          ),
        ],
      ),
    );
  }
  
  Widget _buildStatusMessage(BuildContext context, VoiceManagementState state) {
    final colorScheme = Theme.of(context).colorScheme;
    final isError = state.error != null;
    
    return Container(
      margin: const EdgeInsets.only(top: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isError 
          ? colorScheme.errorContainer.withOpacity(0.3)
          : colorScheme.primaryContainer.withOpacity(0.3),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(
            isError ? Icons.error_outline : Icons.check_circle_outline,
            color: isError ? colorScheme.error : colorScheme.primary,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              state.error ?? state.message ?? '',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: isError 
                  ? colorScheme.onErrorContainer
                  : colorScheme.onPrimaryContainer,
              ),
            ),
          ),
          IconButton(
            onPressed: () => ref.read(voiceManagementProvider.notifier).clearMessage(),
            icon: const Icon(Icons.close),
            iconSize: 16,
          ),
        ],
      ),
    );
  }
  
  Future<void> _pickAudioFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['wav', 'mp3'],
      allowMultiple: false,
    );
    
    if (result != null && result.files.isNotEmpty) {
      setState(() {
        _selectedFilePath = result.files.first.path;
      });
    }
  }
  
  void _addVoice() {
    if (_nameController.text.trim().isEmpty || _selectedFilePath == null) {
      return;
    }
    
    ref.read(voiceManagementProvider.notifier).addVoice(
      name: _nameController.text.trim(),
      filePath: _selectedFilePath!,
    );
    
    // Clear form
    _nameController.clear();
    setState(() {
      _selectedFilePath = null;
    });
  }
  
  void _confirmDeleteVoice(BuildContext context, voice) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Voice'),
        content: Text('Are you sure you want to delete "${voice.name}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              ref.read(voiceManagementProvider.notifier).removeVoice(voice.id);
            },
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
  
  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}