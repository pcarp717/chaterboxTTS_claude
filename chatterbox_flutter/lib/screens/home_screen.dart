import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/audio_player_card.dart';
import '../widgets/text_input_card.dart';
import '../widgets/voice_selection_card.dart';
import '../widgets/system_monitor_card.dart';
import '../widgets/voice_management_card.dart';
import '../widgets/modern_app_bar.dart';
import '../providers/app_providers.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> 
    with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    ));
    
    _fadeController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    
    return Scaffold(
      backgroundColor: colorScheme.surface,
      appBar: const ModernAppBar(),
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: CustomScrollView(
          slivers: [
            // Main content area
            SliverPadding(
              padding: const EdgeInsets.all(24.0),
              sliver: SliverToBoxAdapter(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Left Column - Main controls
                    Expanded(
                      flex: 2,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Hero Section
                          Container(
                            padding: const EdgeInsets.all(32),
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  colorScheme.primaryContainer,
                                  colorScheme.secondaryContainer,
                                ],
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                              ),
                              borderRadius: BorderRadius.circular(24),
                            ),
                            child: Column(
                              children: [
                                Icon(
                                  Icons.record_voice_over,
                                  size: 64,
                                  color: colorScheme.onPrimaryContainer,
                                ),
                                const SizedBox(height: 16),
                                Text(
                                  'ChatterboxTTS Desktop',
                                  style: textTheme.headlineLarge?.copyWith(
                                    color: colorScheme.onPrimaryContainer,
                                    fontWeight: FontWeight.bold,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  'High-quality local text-to-speech with voice cloning',
                                  style: textTheme.bodyLarge?.copyWith(
                                    color: colorScheme.onPrimaryContainer,
                                    opacity: 0.8,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ],
                            ),
                          ),
                          
                          const SizedBox(height: 24),
                          
                          // Text Input Card
                          const TextInputCard(),
                          
                          const SizedBox(height: 20),
                          
                          // Voice Selection Card  
                          const VoiceSelectionCard(),
                          
                          const SizedBox(height: 20),
                          
                          // Audio Player Card
                          const AudioPlayerCard(),
                        ],
                      ),
                    ),
                    
                    const SizedBox(width: 24),
                    
                    // Right Column - Side panels
                    Expanded(
                      flex: 1,
                      child: Column(
                        children: [
                          // System Monitor
                          const SystemMonitorCard(),
                          
                          const SizedBox(height: 20),
                          
                          // Voice Management
                          const VoiceManagementCard(),
                          
                          const SizedBox(height: 20),
                          
                          // Quick Actions Card
                          _buildQuickActionsCard(context),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      
      // Modern Floating Action Button for quick generation
      floatingActionButton: Consumer(
        builder: (context, ref, child) {
          final isGenerating = ref.watch(isGeneratingProvider);
          
          return FloatingActionButton.extended(
            onPressed: isGenerating ? null : () => _generateSpeech(ref),
            icon: isGenerating 
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.mic),
            label: Text(isGenerating ? 'Generating...' : 'Generate'),
            elevation: 6,
          );
        },
      ),
    );
  }
  
  Widget _buildQuickActionsCard(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  Icons.flash_on,
                  color: colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'Quick Actions',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            _buildActionButton(
              context,
              icon: Icons.folder_open,
              label: 'Open Output Folder',
              onTap: () => _openOutputFolder(context),
            ),
            
            const SizedBox(height: 8),
            
            _buildActionButton(
              context,
              icon: Icons.settings,
              label: 'Settings',
              onTap: () => _openSettings(context),
            ),
            
            const SizedBox(height: 8),
            
            _buildActionButton(
              context,
              icon: Icons.info_outline,
              label: 'About',
              onTap: () => _showAbout(context),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildActionButton(
    BuildContext context, {
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        child: Row(
          children: [
            Icon(icon, size: 18),
            const SizedBox(width: 12),
            Text(label),
          ],
        ),
      ),
    );
  }
  
  void _generateSpeech(WidgetRef ref) {
    final textController = ref.read(textControllerProvider);
    final selectedVoice = ref.read(selectedVoiceProvider);
    
    if (textController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter some text to generate speech'),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }
    
    // Trigger TTS generation
    ref.read(ttsServiceProvider).generateSpeech(
      text: textController.text,
      voiceProfile: selectedVoice,
    );
  }
  
  void _openOutputFolder(BuildContext context) {
    // TODO: Implement output folder opening
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Opening output folder...'),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
  
  void _openSettings(BuildContext context) {
    // TODO: Navigate to settings screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Settings coming soon!'),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
  
  void _showAbout(BuildContext context) {
    showAboutDialog(
      context: context,
      applicationName: 'ChatterboxTTS Desktop',
      applicationVersion: '1.0.0',
      applicationIcon: const Icon(
        Icons.record_voice_over,
        size: 48,
      ),
      children: const [
        Text(
          'A modern Flutter desktop application for high-quality '
          'local text-to-speech generation using Resemble AI\'s '
          'Chatterbox TTS model.',
        ),
      ],
    );
  }
}