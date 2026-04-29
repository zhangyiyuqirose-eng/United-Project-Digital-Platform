package com.bank.updg.updg_resource.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_resource.mapper.PersonnelReplacementMapper;
import com.bank.updg.updg_resource.model.entity.PersonnelReplacement;
import com.bank.updg.updg_resource.service.PersonnelReplacementService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PersonnelReplacementServiceImpl extends ServiceImpl<PersonnelReplacementMapper, PersonnelReplacement>
        implements PersonnelReplacementService {

    @Override
    public PersonnelReplacement createReplacement(PersonnelReplacement data) {
        if (data.getReplacementId() == null || data.getReplacementId().isEmpty()) {
            data.setReplacementId(UUID.randomUUID().toString());
        }
        if (data.getStatus() == null) {
            data.setStatus("REQUESTED");
        }
        data.setRequestedAt(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        save(data);
        return data;
    }

    @Override
    public void updateReplacement(String replacementId, PersonnelReplacement data) {
        PersonnelReplacement existing = getById(replacementId);
        if (existing == null) {
            throw new RuntimeException("Replacement not found: " + replacementId);
        }
        if (data.getProjectId() != null) existing.setProjectId(data.getProjectId());
        if (data.getOutgoingStaffId() != null) existing.setOutgoingStaffId(data.getOutgoingStaffId());
        if (data.getIncomingStaffId() != null) existing.setIncomingStaffId(data.getIncomingStaffId());
        if (data.getReason() != null) existing.setReason(data.getReason());
        if (data.getHandoverNotes() != null) existing.setHandoverNotes(data.getHandoverNotes());
        updateById(existing);
    }

    @Override
    public PersonnelReplacement getReplacement(String replacementId) {
        return getById(replacementId);
    }

    @Override
    public Page<PersonnelReplacement> listReplacements(String projectId, String status, int page, int size) {
        Page<PersonnelReplacement> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<PersonnelReplacement> wrapper = new LambdaQueryWrapper<PersonnelReplacement>()
                .orderByDesc(PersonnelReplacement::getRequestedAt);
        if (projectId != null) {
            wrapper.eq(PersonnelReplacement::getProjectId, projectId);
        }
        if (status != null) {
            wrapper.eq(PersonnelReplacement::getStatus, status);
        }
        return page(pageObj, wrapper);
    }

    @Override
    public void approveReplacement(String replacementId) {
        PersonnelReplacement r = getById(replacementId);
        if (r == null) throw new RuntimeException("Replacement not found: " + replacementId);
        r.setStatus("APPROVED");
        updateById(r);
    }

    @Override
    public void completeReplacement(String replacementId) {
        PersonnelReplacement r = getById(replacementId);
        if (r == null) throw new RuntimeException("Replacement not found: " + replacementId);
        r.setStatus("COMPLETED");
        r.setCompletedAt(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        updateById(r);
    }
}
