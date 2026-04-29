package com.bank.updg.updg_business.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_business.model.entity.BusinessOpportunity;

import java.util.List;
import java.util.Map;

public interface BusinessOpportunityService extends IService<BusinessOpportunity> {

    BusinessOpportunity createOpportunity(BusinessOpportunity data);

    void updateOpportunity(String opportunityId, Map<String, Object> data);

    BusinessOpportunity getOpportunity(String opportunityId);

    Page<BusinessOpportunity> listOpportunities(String customerId, String stage, int page, int size);

    void advanceStage(String opportunityId, String nextStage);

    List<Map<String, Object>> getPipeline();
}
