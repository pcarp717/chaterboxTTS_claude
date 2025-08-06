class VoiceProfile {
  final String id;
  final String name;
  final String description;
  final bool isCustom;
  final String? filePath;
  final DateTime? createdAt;
  final double? duration;
  final int? sampleRate;
  
  const VoiceProfile({
    required this.id,
    required this.name,
    required this.description,
    required this.isCustom,
    this.filePath,
    this.createdAt,
    this.duration,
    this.sampleRate,
  });
  
  factory VoiceProfile.fromJson(Map<String, dynamic> json) {
    return VoiceProfile(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      isCustom: json['is_custom'] as bool,
      filePath: json['file_path'] as String?,
      createdAt: json['created_at'] != null 
        ? DateTime.parse(json['created_at'] as String)
        : null,
      duration: json['duration'] as double?,
      sampleRate: json['sample_rate'] as int?,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'is_custom': isCustom,
      'file_path': filePath,
      'created_at': createdAt?.toIso8601String(),
      'duration': duration,
      'sample_rate': sampleRate,
    };
  }
  
  VoiceProfile copyWith({
    String? id,
    String? name,
    String? description,
    bool? isCustom,
    String? filePath,
    DateTime? createdAt,
    double? duration,
    int? sampleRate,
  }) {
    return VoiceProfile(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      isCustom: isCustom ?? this.isCustom,
      filePath: filePath ?? this.filePath,
      createdAt: createdAt ?? this.createdAt,
      duration: duration ?? this.duration,
      sampleRate: sampleRate ?? this.sampleRate,
    );
  }
  
  @override
  String toString() {
    return 'VoiceProfile(id: $id, name: $name, isCustom: $isCustom)';
  }
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is VoiceProfile && other.id == id;
  }
  
  @override
  int get hashCode => id.hashCode;
}