package com.bank.updg.updg_file.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bank.updg.updg_file.mapper.FileInfoMapper;
import com.bank.updg.updg_file.model.entity.FileInfo;
import com.bank.updg.updg_file.service.ArchiveService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * Implementation of document archiving.
 * Marks project files as archived and moves them to the archive bucket.
 */
@Service
@RequiredArgsConstructor
public class ArchiveServiceImpl implements ArchiveService {

    private final FileInfoMapper fileInfoMapper;

    @Override
    public void archiveProjectDocuments(String projectId) {
        LambdaQueryWrapper<FileInfo> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(FileInfo::getProjectId, projectId);
        List<FileInfo> files = fileInfoMapper.selectList(wrapper);

        String archiveBucket = "archive";
        for (FileInfo file : files) {
            // Mark category as archived
            file.setCategory("ARCHIVED");
            // Move to archive bucket
            file.setBucket(archiveBucket);
            fileInfoMapper.updateById(file);
        }
    }
}
