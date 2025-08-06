import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_providers.dart';

class TextInputCard extends ConsumerStatefulWidget {
  const TextInputCard({Key? key}) : super(key: key);

  @override
  ConsumerState<TextInputCard> createState() => _TextInputCardState();
}

class _TextInputCardState extends ConsumerState<TextInputCard> {
  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final textController = ref.watch(textControllerProvider);
    final characterCount = ref.watch(characterCountProvider);
    final isGenerating = ref.watch(isGeneratingProvider);
    
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
                    Icons.edit_note,
                    color: colorScheme.onPrimaryContainer,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'Text Input',
                  style: textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                _buildCharacterCounter(context, characterCount),
              ],
            ),
            
            const SizedBox(height: 20),
            
            // Text input field
            TextField(
              controller: textController,
              maxLines: 8,
              maxLength: 10000,
              enabled: !isGenerating,
              decoration: InputDecoration(
                hintText: 'Enter the text you want to convert to speech...\n\n'
                          'Try something like:\n'
                          '"Hello! This is a test of the ChatterboxTTS system. '
                          'The voice quality is excellent for local generation."',
                hintMaxLines: 6,
                counterText: '', // Hide default counter, we have custom one
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide(
                    color: colorScheme.outline.withOpacity(0.3),
                  ),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide(
                    color: colorScheme.outline.withOpacity(0.3),
                  ),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide(
                    color: colorScheme.primary,
                    width: 2,
                  ),
                ),
                filled: true,
                fillColor: colorScheme.surface,
              ),
              style: textTheme.bodyLarge,
              onChanged: (text) {
                ref.read(characterCountProvider.notifier).state = text.length;
              },
            ),
            
            const SizedBox(height: 16),
            
            // Quick text examples
            _buildQuickExamples(context),
            
            const SizedBox(height: 16),
            
            // Voice settings row
            _buildVoiceSettings(context),
          ],
        ),
      ),
    );
  }
  
  Widget _buildCharacterCounter(BuildContext context, int count) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final isNearLimit = count > 8000;
    final isAtLimit = count >= 10000;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isAtLimit 
          ? colorScheme.errorContainer
          : isNearLimit 
            ? colorScheme.tertiaryContainer
            : colorScheme.secondaryContainer,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        '$count / 10,000',
        style: textTheme.labelMedium?.copyWith(
          color: isAtLimit 
            ? colorScheme.onErrorContainer
            : isNearLimit 
              ? colorScheme.onTertiaryContainer
              : colorScheme.onSecondaryContainer,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
  
  Widget _buildQuickExamples(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    final examples = [
      'Hello, world!',
      'This is a test of the speech synthesis.',
      'The weather today is absolutely beautiful.',
      'Welcome to ChatterboxTTS Desktop!',
    ];
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Examples:',
          style: textTheme.labelLarge?.copyWith(
            fontWeight: FontWeight.w600,
            color: colorScheme.onSurface.withOpacity(0.8),
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: examples.map((example) => _buildExampleChip(context, example)).toList(),
        ),
      ],
    );
  }
  
  Widget _buildExampleChip(BuildContext context, String text) {
    final colorScheme = Theme.of(context).colorScheme;
    
    return ActionChip(
      label: Text(text),
      onPressed: () {
        final controller = ref.read(textControllerProvider);
        controller.text = text;
        ref.read(characterCountProvider.notifier).state = text.length;
      },
      backgroundColor: colorScheme.surfaceVariant,
      side: BorderSide(
        color: colorScheme.outline.withOpacity(0.2),
      ),
      labelStyle: Theme.of(context).textTheme.bodySmall,
      padding: const EdgeInsets.symmetric(horizontal: 8),
    );
  }
  
  Widget _buildVoiceSettings(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final exaggeration = ref.watch(exaggerationProvider);
    final cfgWeight = ref.watch(cfgWeightProvider);
    
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
          Text(
            'Voice Settings',
            style: textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          
          Row(
            children: [
              // Exaggeration slider
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Emotion Level: ${exaggeration.toStringAsFixed(1)}',
                      style: textTheme.labelMedium,
                    ),
                    SliderTheme(
                      data: SliderTheme.of(context).copyWith(
                        trackHeight: 4,
                        thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
                      ),
                      child: Slider(
                        value: exaggeration,
                        min: 0.0,
                        max: 1.0,
                        divisions: 10,
                        onChanged: (value) {
                          ref.read(exaggerationProvider.notifier).state = value;
                        },
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(width: 24),
              
              // CFG Weight slider
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Generation Control: ${cfgWeight.toStringAsFixed(1)}',
                      style: textTheme.labelMedium,
                    ),
                    SliderTheme(
                      data: SliderTheme.of(context).copyWith(
                        trackHeight: 4,
                        thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
                      ),
                      child: Slider(
                        value: cfgWeight,
                        min: 0.0,
                        max: 1.0,
                        divisions: 10,
                        onChanged: (value) {
                          ref.read(cfgWeightProvider.notifier).state = value;
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 8),
          
          // Help text
          Text(
            'Emotion Level controls expressiveness. Generation Control affects text adherence.',
            style: textTheme.bodySmall?.copyWith(
              color: colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
        ],
      ),
    );
  }
}