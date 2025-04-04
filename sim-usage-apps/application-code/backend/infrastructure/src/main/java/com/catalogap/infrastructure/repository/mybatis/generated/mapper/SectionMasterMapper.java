package com.catalogap.infrastructure.repository.mybatis.generated.mapper;

import com.catalogap.infrastructure.repository.mybatis.generated.entity.SectionMaster;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.SectionMasterExample;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SectionMasterMapper {
    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table section_master
     *
     * @mbg.generated
     */
    long countByExample(SectionMasterExample example);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table section_master
     *
     * @mbg.generated
     */
    int deleteByExample(SectionMasterExample example);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table section_master
     *
     * @mbg.generated
     */
    int deleteByPrimaryKey(String sectionId);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table section_master
     *
     * @mbg.generated
     */
    int insert(SectionMaster record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table section_master
     *
     * @mbg.generated
     */
    int insertSelective(SectionMaster record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table section_master
     *
     * @mbg.generated
     */
    List<SectionMaster> selectByExample(SectionMasterExample example);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table section_master
     *
     * @mbg.generated
     */
    SectionMaster selectByPrimaryKey(String sectionId);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table section_master
     *
     * @mbg.generated
     */
    int updateByExampleSelective(@Param("record") SectionMaster record, @Param("example") SectionMasterExample example);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table section_master
     *
     * @mbg.generated
     */
    int updateByExample(@Param("record") SectionMaster record, @Param("example") SectionMasterExample example);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table section_master
     *
     * @mbg.generated
     */
    int updateByPrimaryKeySelective(SectionMaster record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table section_master
     *
     * @mbg.generated
     */
    int updateByPrimaryKey(SectionMaster record);
}