<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Chapter extends Model
{
    protected $fillable = ['title', 'audio_url', 'timings_json'];

    protected $casts = [
        'timings_json' => 'array',
    ];
}
