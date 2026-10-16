"""Tests for RatTeil models."""

import pytest
from datetime import datetime

from ratteil.models import (
    Surah,
    SurahInfo,
    Reciter,
    Moshaf,
    StreamDetails,
    StreamFile,
    StreamStatus,
)


class TestSurah:
    """Tests for Surah model."""
    
    def test_surah_creation(self):
        """Test creating a Surah."""
        surah = Surah(
            id=1,
            name="Al-Fatiha",
            arabic_name="الفاتحة",
            translation="The Opening",
            revelation_type="Meccan",
            verses_count=7,
            pages=[1],
        )
        
        assert surah.id == 1
        assert surah.name == "Al-Fatiha"
        assert surah.arabic_name == "الفاتحة"
        assert surah.verses_count == 7
        assert surah.filename == "001_Al-Fatiha.mp3"
    
    def test_surah_str(self):
        """Test Surah string representation."""
        surah = Surah(
            id=1,
            name="Al-Fatiha",
            arabic_name="الفاتحة",
            translation="The Opening",
            revelation_type="Meccan",
            verses_count=7,
            pages=[1],
        )
        
        assert str(surah) == "Surah 1: Al-Fatiha (الفاتحة)"
    
    def test_surah_repr(self):
        """Test Surah repr."""
        surah = Surah(
            id=1,
            name="Al-Fatiha",
            arabic_name="الفاتحة",
            translation="The Opening",
            revelation_type="Meccan",
            verses_count=7,
            pages=[1],
        )
        
        assert repr(surah) == "Surah(id=1, name='Al-Fatiha')"


class TestSurahInfo:
    """Tests for SurahInfo model."""
    
    def test_surah_info_creation(self):
        """Test creating SurahInfo."""
        surah = Surah(
            id=1,
            name="Al-Fatiha",
            arabic_name="الفاتحة",
            translation="The Opening",
            revelation_type="Meccan",
            verses_count=7,
            pages=[1],
        )
        
        surah_info = SurahInfo(
            surah=surah,
            reciter="Mishary Rashid",
            duration=120.5,
            file_path="/path/to/audio.mp3",
        )
        
        assert surah_info.surah.id == 1
        assert surah_info.reciter == "Mishary Rashid"
        assert surah_info.duration == 120.5
        assert surah_info.file_path == "/path/to/audio.mp3"
    
    def test_surah_info_str(self):
        """Test SurahInfo string representation."""
        surah = Surah(
            id=1,
            name="Al-Fatiha",
            arabic_name="الفاتحة",
            translation="The Opening",
            revelation_type="Meccan",
            verses_count=7,
            pages=[1],
        )
        
        surah_info = SurahInfo(
            surah=surah,
            reciter="Mishary Rashid",
            duration=120.5,
        )
        
        assert "Al-Fatiha" in str(surah_info)
        assert "Mishary Rashid" in str(surah_info)
        assert "120.5s" in str(surah_info)
    
    def test_surah_info_to_dict(self):
        """Test SurahInfo to_dict method."""
        surah = Surah(
            id=1,
            name="Al-Fatiha",
            arabic_name="الفاتحة",
            translation="The Opening",
            revelation_type="Meccan",
            verses_count=7,
            pages=[1],
        )
        
        surah_info = SurahInfo(
            surah=surah,
            reciter="Mishary Rashid",
            duration=120.5,
            file_path="/path/to/audio.mp3",
        )
        
        data = surah_info.to_dict()
        
        assert data["id"] == 1
        assert data["name"] == "Al-Fatiha"
        assert data["reciter"] == "Mishary Rashid"
        assert data["duration"] == 120.5


class TestMoshaf:
    """Tests for Moshaf model."""
    
    def test_moshaf_creation(self):
        """Test creating a Moshaf."""
        moshaf = Moshaf(
            name="Hafs",
            url="https://example.com/audio/{surah_id}.mp3",
            description="Hafs an Asim",
        )
        
        assert moshaf.name == "Hafs"
        assert moshaf.url == "https://example.com/audio/{surah_id}.mp3"
        assert moshaf.moshaf_type.value == "Other"  # Default
    
    def test_moshaf_str(self):
        """Test Moshaf string representation."""
        moshaf = Moshaf(
            name="Hafs",
            url="https://example.com/audio.mp3",
        )
        
        assert "Hafs" in str(moshaf)


class TestReciter:
    """Tests for Reciter model."""
    
    def test_reciter_creation(self):
        """Test creating a Reciter."""
        reciter = Reciter(
            id="alafasy",
            name="Mishary Rashid Alafasy",
            bio="Famous Quran reciter",
            country="Kuwait",
        )
        
        assert reciter.id == "alafasy"
        assert reciter.name == "Mishary Rashid Alafasy"
        assert reciter.bio == "Famous Quran reciter"
        assert reciter.country == "Kuwait"
        assert len(reciter.moshafs) == 0
    
    def test_reciter_add_moshaf(self):
        """Test adding moshaf to reciter."""
        reciter = Reciter(
            id="alafasy",
            name="Mishary Rashid Alafasy",
        )
        
        moshaf = Moshaf(
            name="Hafs",
            url="https://example.com/audio.mp3",
        )
        
        reciter.add_moshaf(moshaf)
        
        assert len(reciter.moshafs) == 1
        assert reciter.moshafs[0].name == "Hafs"
    
    def test_reciter_has_multiple_moshafs(self):
        """Test has_multiple_moshafs method."""
        reciter = Reciter(
            id="alafasy",
            name="Mishary Rashid Alafasy",
        )
        
        assert not reciter.has_multiple_moshafs()
        
        reciter.add_moshaf(Moshaf(name="Hafs", url="url1"))
        assert not reciter.has_multiple_moshafs()
        
        reciter.add_moshaf(Moshaf(name="Warsh", url="url2"))
        assert reciter.has_multiple_moshafs()
    
    def test_reciter_get_moshaf_name_url(self):
        """Test get_moshaf_name_url method."""
        reciter = Reciter(
            id="alafasy",
            name="Mishary Rashid Alafasy",
        )
        
        reciter.add_moshaf(Moshaf(name="Hafs", url="url1"))
        reciter.add_moshaf(Moshaf(name="Warsh", url="url2"))
        
        result = reciter.get_moshaf_name_url()
        
        assert len(result) == 2
        assert ("Hafs", "url1") in result
        assert ("Warsh", "url2") in result
    
    def test_reciter_to_dict(self):
        """Test Reciter to_dict method."""
        reciter = Reciter(
            id="alafasy",
            name="Mishary Rashid Alafasy",
            bio="Famous Quran reciter",
            country="Kuwait",
        )
        
        reciter.add_moshaf(Moshaf(name="Hafs", url="url1"))
        
        data = reciter.to_dict()
        
        assert data["id"] == "alafasy"
        assert data["name"] == "Mishary Rashid Alafasy"
        assert len(data["moshafs"]) == 1


class TestStreamFile:
    """Tests for StreamFile model."""
    
    def test_stream_file_creation(self):
        """Test creating a StreamFile."""
        stream_file = StreamFile(
            path="/path/to/audio.mp3",
            surah_id=1,
            reciter_id="alafasy",
            duration=120.5,
            order=0,
        )
        
        assert stream_file.path == "/path/to/audio.mp3"
        assert stream_file.surah_id == 1
        assert stream_file.reciter_id == "alafasy"
        assert stream_file.duration == 120.5
        assert stream_file.order == 0
    
    def test_stream_file_str(self):
        """Test StreamFile string representation."""
        stream_file = StreamFile(
            path="/path/to/audio.mp3",
            surah_id=1,
            reciter_id="alafasy",
            duration=120.5,
        )
        
        assert "StreamFile" in str(stream_file)
        assert "alafasy" in str(stream_file)


class TestStreamDetails:
    """Tests for StreamDetails model."""
    
    def test_stream_details_creation(self):
        """Test creating StreamDetails."""
        stream_details = StreamDetails(
            title="Test Stream",
            description="Test Description",
        )
        
        assert stream_details.title == "Test Stream"
        assert stream_details.description == "Test Description"
        assert stream_details.total_duration == 0.0
        assert stream_details.status == StreamStatus.PENDING
    
    def test_stream_details_add_file(self):
        """Test adding file to StreamDetails."""
        stream_details = StreamDetails(
            title="Test Stream",
            description="Test Description",
        )
        
        stream_file = StreamFile(
            path="/path/to/audio.mp3",
            surah_id=1,
            reciter_id="alafasy",
            duration=120.5,
        )
        
        stream_details.add_file(stream_file)
        
        assert len(stream_details.stream_files) == 1
        assert stream_details.total_duration == 120.5
    
    def test_stream_details_mark_states(self):
        """Test marking different states."""
        stream_details = StreamDetails(
            title="Test Stream",
            description="Test Description",
        )
        
        assert stream_details.status == StreamStatus.PENDING
        
        stream_details.mark_live()
        assert stream_details.status == StreamStatus.LIVE
        assert stream_details.actual_start is not None
        
        stream_details.mark_completed()
        assert stream_details.status == StreamStatus.COMPLETED
        
        stream_details.mark_error()
        assert stream_details.status == StreamStatus.ERROR
    
    def test_stream_details_get_next_file(self):
        """Test getting next file (FIFO)."""
        stream_details = StreamDetails(
            title="Test Stream",
            description="Test Description",
        )
        
        for i in range(3):
            stream_file = StreamFile(
                path=f"/path/to/audio{i}.mp3",
                surah_id=i,
                reciter_id="alafasy",
                duration=120.5,
                order=i,
            )
            stream_details.add_file(stream_file)
        
        assert len(stream_details.stream_files) == 3
        
        next_file = stream_details.get_next_file()
        assert next_file.path == "/path/to/audio0.mp3"
        assert len(stream_details.stream_files) == 2
    
    def test_stream_details_to_dict(self):
        """Test StreamDetails to_dict method."""
        stream_details = StreamDetails(
            title="Test Stream",
            description="Test Description",
        )
        
        stream_file = StreamFile(
            path="/path/to/audio.mp3",
            surah_id=1,
            reciter_id="alafasy",
            duration=120.5,
        )
        stream_details.add_file(stream_file)
        
        data = stream_details.to_dict()
        
        assert data["title"] == "Test Stream"
        assert data["description"] == "Test Description"
        assert data["total_duration"] == 120.5
        assert len(data["files"]) == 1
