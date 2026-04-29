package com.bank.updg.updg_resource.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_resource.model.entity.PersonnelReplacement;

public interface PersonnelReplacementService extends IService<PersonnelReplacement> {

    PersonnelReplacement createReplacement(PersonnelReplacement data);

    void updateReplacement(String replacementId, PersonnelReplacement data);

    PersonnelReplacement getReplacement(String replacementId);

    Page<PersonnelReplacement> listReplacements(String projectId, String status, int page, int size);

    void approveReplacement(String replacementId);

    void completeReplacement(String replacementId);
}
